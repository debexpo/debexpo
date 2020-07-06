#   test_removeolduploads.py - Test the removeolduploads cronjob
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2020 Baptiste BEAUPLAT <lyknode@cilg.org>
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.
import datetime
import logging
from email import message_from_string
from http.server import BaseHTTPRequestHandler

# from debexpo.lib.email import Email
from debexpo.accounts.models import User
from debexpo.packages.models import Package, PackageUpload, Distribution, \
                                    Component
from tests import TestController, TestingHTTPServer
from debexpo.packages.tasks import remove_old_uploads, remove_uploaded_packages
from debexpo.tools.email import Email

log = logging.getLogger(__name__)
PACKAGE_IN_NEW = '''Source: tmux
Version: 1.0.0
Distribution: unstable

Source: Missing-other-fields'''


class TestCronjobRemoveOldUploads(TestController):
    def setUp(self):
        self._setup_example_user()
        self.state = []

    def tearDown(self):
        Package.objects.all().delete()
        self._remove_example_user()

    def _setup_packages(self, include_expired=False):
        packages = [
                # (package, version, distrib, expired),
                ('htop', '1.0.0', 'unstable', False),
                ('htop', '0.9.0', 'unstable', False),
                ('htop', '0.8.0', 'buster-backports', False),
                ('tmux', '1.0.0', 'unstable', False),
                ('tmux', '1.0.0', 'UNRELEASED', False),
                ('zsh', '1.0.0', 'unstable', False),
                ('zsh', '1.0.0', 'unstable', False),
                ('hello', '1.0.0', 'unstable', True),
                ('hello', '0.9.0', 'unstable', True),
            ]

        for (package, version, distrib, expired) in packages:
            if not expired or (expired and include_expired):
                self._create_package(package, version, distrib, expired)

            if not expired:
                self.state.append((package, version, distrib))

    def _create_package(self, name, version_number, distrib, is_expired):
        date = datetime.datetime.now()
        user = User.objects.first()

        try:
            package = Package.objects.get(name=name)
        except Package.DoesNotExist:
            package = Package(name=name)

        if is_expired:
            date -= datetime.timedelta(days=365)

        package.full_clean()
        package.save()

        upload = PackageUpload(
            package=package,
            version=version_number,
            uploader=user,
            changes='changes',
            distribution=Distribution.objects.get(name=distrib),
            component=Component.objects.get_or_create(name='tools')[0])

        upload.full_clean()
        upload.save()

        PackageUpload.objects.filter(id=upload.id).update(
            uploaded=date.replace(tzinfo=datetime.timezone.utc))

    def _assert_cronjob_success(self):
        packages = Package.objects.all()
        count = 0

        # Each package exists in state
        for package in packages:
            for upload in package.packageupload_set.all():
                log.info('validating {}-{}/{}'.format(package.name,
                                                      upload.version,
                                                      upload.distribution.name))
                self.assertIn((package.name,
                               upload.version,
                               upload.distribution.name), self.state)
                count += 1

        # Each state exists in package
        self.assertEquals(len(self.state), count)

    def _expect_package_removal(self, package_to_remove):
        new_state = []

        for package in self.state:
            if package not in package_to_remove:
                new_state.append(package)

        self.state = new_state

    def remove_upload_accepted(self, uploaded, down=False, garbage=False):
        removed_packages = (
            ('tmux', '1.0.0', 'unstable'),
            ('tmux', '1.0.0', 'UNRELEASED'),
        )

        self._expect_package_removal(removed_packages)
        with TestingHTTPServer(FTPMasterPackageInNewHTTPHandler) as httpd:
            with self.settings(
                    FTP_MASTER_NEW_PACKAGES_URL='http://localhost:'
                                                f'{httpd.port}'):
                remove_uploaded_packages(FakeNNTPClient(uploaded, down,
                                                        garbage))

    def test_package_in_new_server_error(self):
        with TestingHTTPServer(FTPMasterPackageInNewErrorHTTPHandler) as httpd:
            with self.settings(
                    FTP_MASTER_NEW_PACKAGES_URL='http://localhost:'
                                                f'{httpd.port}'):
                remove_uploaded_packages(FakeNNTPClient([]))
        self._assert_cronjob_success()

    def test_remove_uploads_noop_no_packages(self):
        remove_old_uploads()
        self._assert_cronjob_success()

    def test_remove_uploads_server_down(self):
        self.remove_upload_accepted([], True)
        self._assert_cronjob_success()

    def test_remove_uploads_server_garbage(self):
        self.remove_upload_accepted([], False, True)
        self._assert_cronjob_success()

    def test_remove_uploads_inexistant_package(self):
        self.remove_upload_accepted([('inexistant_package', '1.0.0',
                                      'unstable')])
        self._assert_cronjob_success()

    def test_remove_uploads_noop_with_packages(self):
        self._setup_packages()
        remove_old_uploads()
        self._assert_cronjob_success()

    def test_remove_uploads_expired(self):
        self._setup_packages(include_expired=True)
        remove_old_uploads()
        self._assert_cronjob_success()

    def test_remove_uploads_keep_other_dists(self):
        removed_packages = [
                ('htop', '1.0.0', 'unstable'),
                ('htop', '0.9.0', 'unstable'),
            ]

        self._setup_packages()
        self.remove_upload_accepted([('htop', '1.0.0', 'unstable')])
        self._expect_package_removal(removed_packages)
        self._assert_cronjob_success()

    def test_remove_uploads_same_version(self):
        removed_packages = [
                ('zsh', '1.0.0', 'unstable'),
            ]

        self._setup_packages()
        self.remove_upload_accepted([('zsh', '1.0.0', 'unstable')])
        self._expect_package_removal(removed_packages)
        self._assert_cronjob_success()

    def test_remove_uploads_keep_newer(self):
        removed_packages = [
                ('htop', '0.9.0', 'unstable'),
            ]

        self._setup_packages()
        self.remove_upload_accepted([('htop', '0.9.0', 'unstable')])
        self._expect_package_removal(removed_packages)
        self._assert_cronjob_success()


class FTPMasterPackageInNewHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(bytes(PACKAGE_IN_NEW, 'UTF-8'))


class FTPMasterPackageInNewErrorHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(500, 'Internal Server Error')
        self.end_headers()


class FakeNNTPClient():
    def __init__(self, uploads, down=False, garbage=False):
        self.uploads = uploads
        self.iter = 0
        self.down = down
        self.garbage = garbage

    def connect_to_server(self):
        return not self.down

    def disconnect_from_server(self):
        return True

    def unread_messages(self, name, last):
        self.iter += 1

        if self.iter == 1:
            if self.garbage:
                for item in [None,
                             message_from_string('Subject: test\n\ntest')]:
                    yield item
            else:
                for upload in self.uploads:
                    yield self._build_nntp_response(upload)

    def _build_nntp_response(self, upload):
        email = Email('test-upload-accepted.html')
        body = message_from_string(email._render_content([], **{
            'name': upload[0],
            'version': upload[1],
            'distrib': upload[2],
        }))
        body['X-Debexpo-Message-Number'] = 42

        return body

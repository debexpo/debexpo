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

# from debexpo.lib.email import Email
from debexpo.accounts.models import User
from debexpo.packages.models import Package, PackageUpload, Distribution, \
                                    Component
from tests import TestController
from debexpo.packages.tasks import remove_old_uploads

log = logging.getLogger(__name__)


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

    def _invoke_plugin(self, uploaded):
        remove_old_uploads()

    def test_remove_uploads_noop_no_packages(self):
        self._invoke_plugin([])
        self._assert_cronjob_success()

    # def test_remove_uploads_inexistant_package(self):
    #     self._invoke_plugin([('inexistant_package', '1.0.0', 'unstable')])
    #     self._assert_cronjob_success()

    def test_remove_uploads_noop_with_packages(self):
        self._setup_packages()
        self._invoke_plugin([])
        self._assert_cronjob_success()

    def test_remove_uploads_expired(self):
        self._setup_packages(include_expired=True)
        self._invoke_plugin([])
        self._assert_cronjob_success()

    # def test_remove_uploads_keep_other_dists(self):
    #     removed_packages = [
    #             ('htop', '1.0.0', 'unstable'),
    #             ('htop', '0.9.0', 'unstable'),
    #         ]

    #     self._setup_packages()
    #     self._invoke_plugin([('htop', '1.0.0', 'unstable')])
    #     self._expect_package_removal(removed_packages)
    #     self._assert_cronjob_success()

    # def test_remove_uploads_same_version(self):
    #     removed_packages = [
    #             ('zsh', '1.0.0', 'unstable'),
    #         ]

    #     self._setup_packages()
    #     self._invoke_plugin([('zsh', '1.0.0', 'unstable')])
    #     self._expect_package_removal(removed_packages)
    #     self._assert_cronjob_success()

    # def test_remove_uploads_keep_newer(self):
    #     removed_packages = [
    #             ('htop', '0.9.0', 'unstable'),
    #         ]

    #     self._setup_packages()
    #     self._invoke_plugin([('htop', '0.9.0', 'unstable')])
    #     self._expect_package_removal(removed_packages)
    #     self._assert_cronjob_success()

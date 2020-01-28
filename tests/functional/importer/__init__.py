#   test_upload.py — UploadController test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2018-2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

import logging
import socket

from os import walk
from os.path import isdir, join, dirname
from shutil import rmtree, copytree
from tempfile import TemporaryDirectory

from django.core import mail
from django_redis.pool import ConnectionFactory

from debexpo.importer.models import Importer, Spool
from debexpo.packages.models import Package, PackageUpload
from debexpo.accounts.models import User
from debexpo.comments.models import PackageSubscription
from tests import TestController
from tests.functional.importer.source_package import TestSourcePackage

log = logging.getLogger(__name__)


def test_network():
    socket.setdefaulttimeout(2)

    try:
        socket.gethostbyname('bugs.debian.org')
    except socket.error as e:
        return e

    return None


class FakeConnectionFactory(ConnectionFactory):
    def get_connection(self, params):
        return self.redis_client_cls(**self.redis_client_cls_kwargs)


class TestImporterController(TestController):
    """
    Toolbox for importer tests

    This class setup an environment for package to be imported in and ensure
    cleanup afterward.
    """

    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)
        self.data_dir = join(dirname(__file__), 'data')

    def setUp(self):
        self._setup_example_user(gpg=True)
        self.spool_dir = TemporaryDirectory(prefix='debexpo-test-spool')
        self.repository_dir = TemporaryDirectory(prefix='debexpo-test-repo')
        self.repository = self.repository_dir.name
        self.spool = Spool(self.spool_dir.name)

    def tearDown(self):
        self._assert_no_leftover()
        self._remove_subscribers()
        self._remove_example_user()
        self._cleanup_package()

    def _remove_subscribers(self):
        PackageSubscription.objects.all().delete()

    def setup_subscribers(self, package, on_upload=True, on_comment=False):
        user = User.objects.get(email='email@example.com')

        subscription = PackageSubscription(package=package, user=user,
                                           on_upload=on_upload,
                                           on_comment=on_comment)
        subscription.save()

    def _cleanup_mailbox(self):
        mail.outbox = []

    def _upload_package(self, package_dir):
        """Copy a directory content to incoming queue"""
        # copytree dst dir must not exist
        upload_dir = self.spool.get_queue_dir('incoming')

        if isdir(upload_dir):
            rmtree(upload_dir)
        copytree(package_dir, upload_dir)

    def _get_email(self):
        """Parse an email and format the body."""
        return mail.outbox[0].body

    def _cleanup_package(self):
        Package.objects.all().delete()

    def _assert_no_leftover(self):
        matches = self._find_all('', str(self.spool))
        log.error(f'matches for {str(self.spool)} {matches}')

        for match in matches:
            log.debug('leftover: {}'.format(match))

        self.assertFalse(matches)

    def _package_in_repo(self, package_name, version):
        """Check if package is present in repo"""
        matches = self._find_file(package_name + '_' + version + '.dsc',
                                  self.repository)
        return len(matches)

    def _file_in_repo(self, filename):
        """Check if package is present in repo"""
        matches = self._find_file(filename,
                                  self.repository)
        return len(matches)

    def _find_file(self, name, path):
        """Find a file in a path"""
        result = []
        for root, dirs, files in walk(path):
            if name in files:
                result.append(join(root, name))
        return result

    def _find_all(self, name, path):
        """Find a file in a path"""
        result = []
        for root, dirs, files in walk(path):
            for filename in files:
                if name in filename:
                    result.append(join(root, filename))
        return result

    def import_source_package(self, package_dir, skip_gpg=False,
                              skip_email=False):
        source_package = TestSourcePackage(package_dir)

        source_package.build()
        self._run_importer(source_package.get_package_dir(), skip_gpg=skip_gpg,
                           skip_email=skip_email)

    def import_package(self, package_dir):
        self._run_importer(join(self.data_dir, package_dir))

    def _run_importer(self, package_dir, skip_gpg=False, skip_email=False):
        """Run debexpo importer on package_dir/*.changes"""
        # Copy uplod files to incomming queue
        self.assertTrue(isdir(package_dir))
        self._upload_package(package_dir)

        # Run the importer on change file
        importer = Importer(str(self.spool), self.repository,
                            skip_email, skip_gpg)
        self._status_importer = importer.process_spool()

    def assert_importer_failed(self):
        """Assert that the importer has failed"""
        self.assertFalse(self._status_importer)

    def assert_importer_succeeded(self):
        """Assert that the importer has succeeded"""
        self.assertTrue(self._status_importer)

    def assert_no_email(self):
        """Assert that the importer has not generated any email"""
        # The mailbox file has not been created
        self.assertFalse(mail.outbox)

    def assert_email_with(self, search_text):
        """
        Assert that the imported would have sent a email to the uploader
        containing search_text
        """
        # The mailbox file has been created
        self.assertTrue(mail.outbox)

        # Get the email and assert that the body contains search_text
        email = self._get_email()
        self.assertIn(search_text, email)

    def assert_package_count(self, package_name, version, count):
        """Assert that a package appears count times in debexpo"""
        try:
            package = Package.objects.get(name=package_name)
        except Package.DoesNotExist:
            count_in_db = 0
        else:
            count_in_db = PackageUpload.objects \
                .filter(package=package) \
                .filter(version=version) \
                .count()

        self.assertTrue(count_in_db == count)

    def _lookup_package_info(self, package_name, plugin):
        pass
        # package = meta.session.query(Package).filter(Package.name ==
        #                                              package_name).first()
        # package_version = meta.session.query(PackageVersion) \
        #     .filter(PackageVersion.package_id == package.id) \
        #     .first()
        # package_info = meta.session.query(PackageInfo) \
        #     .filter(PackageInfo.package_version_id == package_version.id) \
        #     .filter(PackageInfo.from_plugin == plugin).first()

        # return package_info

    def assert_package_no_info(self, package_name, plugin):
        pass
        # package_info = self._lookup_package_info(package_name, plugin)
        # self.assertFalse(package_info)

    def assert_package_info(self, package_name, plugin, outcome):
        pass
        # package_info = self._lookup_package_info(package_name, plugin)
        # self.assertTrue(package_info)
        # self.assertEquals(outcome, package_info.outcome)

    def assert_package_severity(self, package_name, plugin, severity):
        pass
        # package_info = self._lookup_package_info(package_name, plugin)
        # self.assertTrue(package_info)
        # self.assertTrue(severity == package_info.severity)

    def assert_package_data(self, package_name, plugin, data):
        pass
        # package_info = self._lookup_package_info(package_name, plugin)
        # self.assertTrue(package_info)
        # self.assertTrue(data in package_info.data)

    def assert_file_in_repo(self, filename):
        """Assert that a file is present in debexpo repo"""
        log.debug('Checking file in repo: {}'.format(filename))
        self.assertTrue(self._file_in_repo(filename) > 0)

    def assert_package_in_repo(self, package_name, version):
        """Assert that a package is present in debexpo repo"""
        self.assertTrue(self._package_in_repo(package_name, version) > 0)

    def assert_package_not_in_repo(self, package_name, version):
        """Assert that a package is present in debexpo repo"""
        self.assertTrue(self._package_in_repo(package_name, version) == 0)

    def assert_rfs_content(self, package, content):
        pass
        # response = self.app.get(url(controller='sponsors', action='rfs-howto',
        #                             id=package))
        # self.assertEquals(response.status_int, 200)
        # log.debug('rfs: {}'.format(response))
        # self.assertTrue(content in response)

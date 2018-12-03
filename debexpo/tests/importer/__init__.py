# -*- coding: utf-8 -*-
#
#   test_upload.py — UploadController test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2018 Baptiste BEAUPLAT <lyknode@cilg.org>
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

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2018 Baptiste BEAUPLAT'
__license__ = 'MIT'

import pylons

from email import message_from_file
from glob import glob
from os import remove
from os.path import isdir, isfile, join, dirname
from shutil import rmtree, copytree
from subprocess import Popen, PIPE

from bin.debexpo_importer import Importer
from debexpo.model import meta
from debexpo.model.package_versions import PackageVersion
from debexpo.model.packages import Package
from debexpo.tests import TestController, url

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
        self._setup_models()
        self._setup_example_user(gpg=True)
        self._cleanup_mailbox()
        self._cleanup_repo()

    def tearDown(self):
        self._remove_example_user()
        self._cleanup_mailbox()
        self._cleanup_repo()

    def _cleanup_mailbox(self):
        """Delete mailbox file"""
        if 'debexpo.testsmtp' in pylons.config:
            if isfile(pylons.config['debexpo.testsmtp']):
                remove(pylons.config['debexpo.testsmtp'])

    def _cleanup_repo(self):
        """Delete all files present in repo directory"""
        if 'debexpo.repository' in pylons.config:
            if isdir(pylons.config['debexpo.repository']):
                rmtree(pylons.config['debexpo.repository'])

    def _upload_package(self, package_dir):
        """Copy a directory content to incoming queue"""
        self.assertTrue('debexpo.upload.incoming' in pylons.config)
        self.upload_dir = pylons.config['debexpo.upload.incoming']

        # copytree dst dir must not exist
        if isdir(self.upload_dir):
            rmtree(self.upload_dir)
        copytree(join(self.data_dir, package_dir), self.upload_dir)

    def _get_email(self):
        """Parse an email and format the body."""
        email = None

        # Load mailbox
        with open(pylons.config['debexpo.testsmtp'], 'r') as mbox:
            email = message_from_file(mbox)
        return email

    def import_package(self, package_dir):
        """Run debexpo importer on package_dir/*.changes"""
        # Copy uplod files to incomming queue
        self.assertTrue(isdir(join(self.data_dir, package_dir)))
        self._upload_package(package_dir)

        # Get change file
        matches = glob(join(self.upload_dir, '*.changes'))
        self.assertTrue(len(matches) == 1)
        changes = matches[0]

        # Run the importer on change file
        importer = Importer(changes, pylons.config['global_conf']['__file__'],
                False, False)
        self._status_importer = importer.main(no_env=True)

    def assert_importer_failed(self):
        """Assert that the importer has failed"""
        self.assertFalse(self._status_importer == 0)

    def assert_importer_succeeded(self):
        """Assert that the importer has succeeded"""
        self.assertTrue(self._status_importer == 0)

    def assert_no_email(self):
        """Assert that the importer has not generated any email"""
        # This check only works when a file mailbox is configured
        self.assertTrue('debexpo.testsmtp' in pylons.config)

        # The mailbox file has not been created
        self.assertFalse(isfile(pylons.config['debexpo.testsmtp']))

    def assert_email_with(self, search_text):
        """
        Assert that the imported would have sent a email to the uploader
        containing search_text
        """
        # This check only works when a file mailbox is configured
        self.assertTrue('debexpo.testsmtp' in pylons.config)

        # The mailbox file has been created
        self.assertTrue(isfile(pylons.config['debexpo.testsmtp']))

        # Get the email and assert that the body contains search_text
        email = self._get_email()
        self.assertTrue(search_text in email.get_payload(decode=True))

    def assert_package_count(self, package_name, version, count):
        """
        Assert that a package appears count times in debexpo

        If count > 0, this method with also assert that the package is present
        in debexpo repository.
        """
        package = meta.session.query(Package).filter(Package.name ==
                package_name).all()
        if package:
            count_in_db = \
            meta.session.query(PackageVersion).filter(PackageVersion.package_id
                    == version and PackageVersion.version == version).count()
        else:
            count_in_db = 0
        self.assertTrue(count_in_db == count)

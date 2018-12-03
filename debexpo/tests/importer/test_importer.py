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

"""
UploadController test cases.
"""

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2018 Baptiste BEAUPLAT'
__license__ = 'MIT'

from pylons.test import pylonsapp
from debexpo.tests.importer import TestImporterController

class TestImporter(TestImporterController):
    """
    This class tests debexpo's importer.

    Its goal is to process a user upload, validate it and reject it with a email
    sent to the user or accepting it and making it available in debexpo repo
    """

    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def test_import_package_empty_changes(self):
        self.import_package('emtpy-changes')
        self.assert_importer_failed()
        self.assert_no_email()
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_corrupted_changes(self):
        self.import_package('corrupted-changes')
        self.assert_importer_failed()
        self.assert_no_email()
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_missing_file_in_changes(self):
        self.import_package('missing-file-in-changes')
        self.assert_importer_failed()
        self.assert_no_email()
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_wrong_checksum_in_changes(self):
        self.import_package('wrong-checksum-in-changes')
        self.assert_importer_failed()
        self.assert_no_email()
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_no_dsc(self):
        self.import_package('no-dsc')
        self.assert_importer_failed()
        self.assert_email_with('Rejecting incomplete upload.\nYou did not'
                ' upload the dsc file\n')
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_not_signed(self):
        self.import_package('not-signed')
        self.assert_importer_failed()
        self.assert_email_with('Your upload does not appear to be signed')
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_unknown_key(self):
        self.import_package('unknown-key')
        self.assert_importer_failed()
        self.assert_email_with('Your upload does not contain a valid'
                ' signature.')
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_wrong_gpg_uid(self):
        self.import_package('wrong-gpg-uid')
        self.assert_importer_failed()
        self.assert_email_with('Your GPG key does not match the email used to'
                ' register')
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_invalid_dist(self):
        self.import_package('invalid-dist')
        self.assert_importer_failed()
        self.assert_email_with('You are not uploading to one of those Debian'
                ' distribution')
        self.assert_package_count('hello', '1.0-1', 0)

    def test_import_package_no_orig(self):
        self.import_package('no-orig')
        self.assert_importer_failed()
        self.assert_email_with('Rejecting incomplete upload. You did not'
                ' upload any original tarball (orig.tar.gz)')
        self.assert_package_count('non-existent', '1.0-1', 0)

    def test_import_package_debian_orig_too_big(self):
        self.import_package('debian-orig-too-big')
        self.assert_importer_failed()
        self.assert_email_with('We did find it on Debian main archive, however'
                ' it is too big to be downloaded by our system')
        self.assert_package_count('0ad-data', '0.0.23-1', 0)

    def test_import_package_hello(self):
        self.import_package('hello')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                + pylonsapp.config['debexpo.sitename'] + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 1)

        self._cleanup_mailbox()
        self.import_package('hello')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                + pylonsapp.config['debexpo.sitename'] + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 2)

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

    _ORPHAN_GPG_KEY = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEW/F8GBYJKwYBBAHaRw8BAQdA6Riq9GZh/HiwtFjPcvz5i5oFzp1I8RiqxBs1
g06oSh+0HXByaW1hcnkgaWQgPG1haW5AZXhhbXBsZS5vcmc+iJMEExYIADsCGwMF
CwkIBwIGFQoJCAsCBBYCAwECHgECF4AWIQSGVz4uSUdVmCPsPxTH4ZqYGuqOuwUC
W/F8dAIZAQAKCRDH4ZqYGuqOu9GTAQCCMRbXuueDLcC4eWmMGGiAmqLzKdhGJxQe
e0k5d6wkKQEA2vdlMg9s3UFL4e8jnJPYeNpsxDaaEPr0jMLnwcBp8wa0JWRlYmV4
cG8gdGVzdGluZyA8ZGViZXhwb0BleGFtcGxlLm9yZz6IkAQTFggAOBYhBIZXPi5J
R1WYI+w/FMfhmpga6o67BQJb8XxSAhsDBQsJCAcCBhUKCQgLAgQWAgMBAh4BAheA
AAoJEMfhmpga6o67MjUBAMYVSthPo3oKR1PpV9ebHFiSARmc2BxxL+xmdzfiRT3O
AP9JQZxCSl3awI5xos8mw2edsDWYcaS2y+RmbTLv8wR2Abg4BFvxfBgSCisGAQQB
l1UBBQEBB0Doc/H7Tyvf+6kdlnUOqY+0t3pkKYj0EOK6QFKMnlRpJwMBCAeIeAQY
FggAIBYhBIZXPi5JR1WYI+w/FMfhmpga6o67BQJb8XwYAhsMAAoJEMfhmpga6o67
Vh8A/AxTKLqACJnSVFrO2sArc7Yt3tymB+of9JeBF6iYBbuDAP9r32J6TYFB9OSz
r1JREXlgQRuRdd5ZWSvIxKaKGVbYCw==
=BMLr
-----END PGP PUBLIC KEY BLOCK-----
"""

    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def test_import_package_empty_changes(self):
        self.import_package('emtpy-changes')
        self.assert_importer_failed()
        self.assert_no_email()
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_corrupted_changes(self):
        self.import_package('corrupted-changes')
        self.assert_importer_failed()
        self.assert_no_email()
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_missing_file_in_changes(self):
        self.import_package('missing-file-in-changes')
        self.assert_importer_failed()
        self.assert_email_with('Missing file hello_1.0-1.debian.tar.xz in'
                               ' incoming')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_wrong_checksum_in_changes(self):
        self.import_package('wrong-checksum-in-changes')
        self.assert_importer_failed()
        self.assert_email_with('MD5 sum mismatch in file hello_1.0-1.dsc:')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_no_dsc(self):
        self.import_package('no-dsc')
        self.assert_importer_failed()
        self.assert_email_with('Rejecting incomplete upload.\nYou did not'
                               ' upload the dsc file\n')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_not_signed(self):
        self.import_package('not-signed')
        self.assert_importer_failed()
        self.assert_email_with('Your upload does not appear to be signed')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_unknown_key(self):
        self.import_package('unknown-key')
        self.assert_importer_failed()
        self.assert_email_with('Your upload does not contain a valid'
                               ' signature.')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_wrong_gpg_uid(self):
        self._add_gpg_key(self._ORPHAN_GPG_KEY)
        self.import_package('wrong-gpg-uid')
        self.assert_importer_failed()
        self.assert_email_with('Your GPG key does not match the email used to'
                               ' register')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_invalid_dist(self):
        self.import_package('invalid-dist')
        self.assert_importer_failed()
        self.assert_email_with('You are not uploading to one of those Debian'
                               ' distribution')
        self.assert_package_count('hello', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_no_orig(self):
        self.import_package('no-orig')
        self.assert_importer_failed()
        self.assert_email_with('error: missing orig.tar or debian.tar file in'
                               ' v2.0 source package')
        self.assert_package_count('non-existent', '1.0-1', 0)
        self.assert_package_not_in_repo('hello', '1.0-1')

    def test_import_package_debian_orig_too_big(self):
        self.import_package('debian-orig-too-big')
        self.assert_importer_failed()
        self.assert_email_with('The original tarball cannot be retrieved from'
                               ' Debian: file too big (> 100MB)')
        self.assert_package_count('0ad-data', '0.0.23.1-1.1', 0)
        self.assert_package_not_in_repo('0ad-data', '0.0.23.1-1.1')

    def test_import_package_mismatch_orig_official(self):
        self.import_package('mismatch-orig')
        self.assert_importer_failed()
        self.assert_email_with('Orig tarball used in the Dsc does not match'
                               ' orig present in the archive')
        self.assert_package_count('htop', '2.2.0-1+b1', 0)
        self.assert_package_not_in_repo('htop', '2.2.0-1+b1')

    def test_import_package_hello_unicode(self):
        self.import_package('unicode-changes')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                               + pylonsapp.config['debexpo.sitename']
                               + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 1)
        self.assert_package_in_repo('hello', '1.0-1')
        self.assert_package_info('hello', 'debianqa',
                                 'Package is already in Debian')

    def test_import_package_hello(self):
        self.import_package('hello')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                               + pylonsapp.config['debexpo.sitename']
                               + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 1)
        self.assert_package_in_repo('hello', '1.0-1')

        self._cleanup_mailbox()
        self.import_package('hello')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'hello' to "
                               + pylonsapp.config['debexpo.sitename']
                               + " was\nsuccessful.")
        self.assert_package_count('hello', '1.0-1', 2)
        self.assert_package_in_repo('hello', '1.0-1')

    def test_import_package_htop_download_orig(self):
        self.import_package('orig-from-official')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'htop' to "
                               + pylonsapp.config['debexpo.sitename']
                               + " was\nsuccessful.")
        self.assert_package_count('htop', '2.2.0-1+b1', 1)
        self.assert_package_in_repo('htop', '2.2.0-1')

        self._cleanup_mailbox()
        self.import_package('orig-from-official')
        self.assert_importer_succeeded()
        self.assert_email_with("Your upload of the package 'htop' to "
                               + pylonsapp.config['debexpo.sitename']
                               + " was\nsuccessful.")
        self.assert_package_count('htop', '2.2.0-1+b1', 2)
        self.assert_package_in_repo('htop', '2.2.0-1')

# -*- coding: utf-8 -*-
#
#   utils.py — Debexpo utility functions
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Serafeim Zanikolas <serzan@hellug.gr>
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
Test cases for debexpo.lib.gnupg.
"""

__author__ = 'Serafeim Zanikolas'
__copyright__ = 'Copyright © 2008 Serafeim Zanikolas'
__license__ = 'MIT'

from unittest import TestCase
import os

from pylons import config

from debexpo.lib.gnupg import GnuPG

test_gpg_key = \
"""-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEW9b91RYJKwYBBAHaRw8BAQdAHtUIQWAsmPilu0JDMnLbpPQfT1i3z2IVMoDH
rhlYkO+0JWRlYmV4cG8gdGVzdGluZyA8ZGViZXhwb0BleGFtcGxlLm9yZz6IkAQT
FggAOBYhBOF57qTrR+YF2YZjLihiGOfHT5wRBQJb1v3VAhsDBQsJCAcCBhUKCQgL
AgQWAgMBAh4BAheAAAoJEChiGOfHT5wRdQIBAJ8rciR0e1PaA+LhoTWHaPSgCwvc
lNFyRk71s75+hRkhAPwPnl6QqGsOa0DyJB5saVcqPCqYFbF1usUWIQnPPRsVC7g4
BFvW/dUSCisGAQQBl1UBBQEBB0DzrYDCp+OaNFinqKkDWcqftqq/BAFS9lq4de5g
RNytNAMBCAeIeAQYFggAIBYhBOF57qTrR+YF2YZjLihiGOfHT5wRBQJb1v3VAhsM
AAoJEChiGOfHT5wRNK8A/115pc8+OwKDy1fGXGX3l0uq1wdfiJreG/9YZddx/JTI
AQD4ZLpyUg+z6kJ+8YAmHFiOD9Ixv3QVvrfpBwnBVtJZBg==
=N+9W
-----END PGP PUBLIC KEY BLOCK-----
"""

test_gpg_key_id = '256E/C74F9C11'
test_gpg_key_name = 'debexpo testing'
test_gpg_key_email = 'debexpo@example.org'

class TestGnuPGController(TestCase):

    def _get_gnupg(self, gpg_path='/usr/bin/gpg'):
        config['debexpo.gpg_path'] = gpg_path
        gnupg = GnuPG() # instantiate with new debexpo.gpg_path setting
        return gnupg

    def testGnuPGfailure1(self):
        """
        Test for debexpo.gpg_path being uninitialised.
        """
        gnupg = self._get_gnupg(None)
        self.assertTrue(gnupg.is_unusable())

    def testGnuPGfailure2(self):
        """
        Test for debexpo.gpg_path pointing to a non-existent file.
        """
        gnupg = self._get_gnupg('/non/existent')
        self.assertTrue(gnupg.is_unusable())

    def testGnuPGfailure3(self):
        """
        Test for debexpo.gpg_path pointing to a non-executable file.
        """
        gnupg = self._get_gnupg('/etc/passwd')
        self.assertTrue(gnupg.is_unusable())

    def testParseKeyID(self):
        """
        Test the extraction of key id from a given GPG key.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        (gpg_key_id, _) = gnupg.parse_key_id(test_gpg_key)
        self.assertEqual(gpg_key_id, test_gpg_key_id)

    def testParseKeyIDWithUID(self):
        """
        Test the extraction of an uid from a given GPG key.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        (_, gpg_key_uids) = gnupg.parse_key_id(test_gpg_key)
        (gpg_key_name, gpg_key_email) = gpg_key_uids[0]
        self.assertEqual(gpg_key_name, test_gpg_key_name)
        self.assertEqual(gpg_key_email, test_gpg_key_email)

    def testSignatureVerification(self):
        """
        Verify the signature in the file debexpo/tests/gpg/debian_announcement.gpg.asc.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        gpg_data_dir = os.path.join(os.path.dirname(__file__), 'gpg')
        signed_file = os.path.join(gpg_data_dir, 'debian_announcement.gpg.asc')
        pubring = os.path.join(gpg_data_dir, 'pubring.gpg')
        assert os.path.exists(signed_file)
        assert os.path.exists(pubring)
        self.assertTrue(gnupg.verify_sig(signed_file, pubring))

    def testSignatureVerificationWithUID(self):
        """
        Verify the signature in the file debexpo/tests/gpg/debian_announcement.gpg.asc.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        gpg_data_dir = os.path.join(os.path.dirname(__file__), 'gpg')
        signed_file = os.path.join(gpg_data_dir, 'debian_announcement.gpg.asc')
        pubring = os.path.join(gpg_data_dir, 'pubring.gpg')
        assert os.path.exists(signed_file)
        assert os.path.exists(pubring)
        (out, uids, status) = gnupg.verify_sig_full(signed_file, pubring)
        self.assertEquals(status, 0)
        self.assertTrue(('debexpo testing', 'debexpo@example.org') in uids)

    def testInvalidSignature(self):
        """
        Test that verify_sig() fails for an unsigned file.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        self.assertFalse(gnupg.verify_sig('/etc/passwd'))

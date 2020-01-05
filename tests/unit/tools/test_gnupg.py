#   test_gnupg.py - Unit testing for GnuPG helpers
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Serafeim Zanikolas <serzan@hellug.gr>
#               2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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
Test cases for debexpo.tools.gnupg
"""

import os

from django.test import TestCase
from django.conf import settings

from debexpo.tools.gnupg import GnuPG, ExceptionGnuPGNotSignedFile, \
    ExceptionGnuPG, ExceptionGnuPGNoPubKey, ExceptionGnuPGPathNotInitialized

test_gpg_key = """-----BEGIN PGP PUBLIC KEY BLOCK-----

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
-----END PGP PUBLIC KEY BLOCK-----"""

test_multi_gpg_key = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEXLTbcxYJKwYBBAHaRw8BAQdAoh3VCQpeRnjWSsGxL8TmOE6AOc5W/3BGt+TH
NlTNv2e0LVZpbmNlbnQgVElNRSAoVEVTVElORyBLRVkgMSkgPHZ0aW1lQGNpbGcu
b3JnPoiQBBMWCAA4FiEE2QTvCDJA2cJrCuaBNkkwohbvF/0FAly023MCGwMFCwkI
BwIGFQoJCAsCBBYCAwECHgECF4AACgkQNkkwohbvF/24QgEAhjlLjQzHSR7xR4+I
i0KVuRBw9gTiLGN80UVt8s0ONGEA/3Ft1HQ5b37rFSY44Yvnuv8ejdTMqhO0sZ0J
3OKTuVcBuDgEXLTbcxIKKwYBBAGXVQEFAQEHQBQ1AKhzJ+miI9wlpeTPfKzbYPIb
fN3+uHMNRAsP0zoaAwEIB4h4BBgWCAAgFiEE2QTvCDJA2cJrCuaBNkkwohbvF/0F
Aly023MCGwwACgkQNkkwohbvF/0hGAEAxkUFu5BAKwEToaoLs/0sePvL0S+EnR7F
b0uzAD7qCN0BAKEKKL6PoMD5cwSlaN1j6z3K5UbPvkMulGXK38vt110LmDMEXLTb
lxYJKwYBBAHaRw8BAQdA0nglRFeDWhHZq7a9UfIjLyupPutx9DL7+qk+Wfml0Uy0
LVZpbmNlbnQgVElNRSAoVEVTVElORyBLRVkgMikgPHZ0aW1lQGNpbGcub3JnPoiQ
BBMWCAA4FiEEdLUyC8hsXaia62wnbaTvWsnriSoFAly025cCGwMFCwkIBwIGFQoJ
CAsCBBYCAwECHgECF4AACgkQbaTvWsnriSpQCwEA5sJ8Bfm1BMwhMZet53o5k74t
X6P/piUOFeifO/c6tQ0A/33bE2W/7m9S8SJzcsin9ISEOSV2Z2dPQhCPj8afu+EC
uDgEXLTblxIKKwYBBAGXVQEFAQEHQPuCyECR7wFvp1wKwzBMK/bBMi/UFxeh0qoZ
GdQ6ChBXAwEIB4h4BBgWCAAgFiEEdLUyC8hsXaia62wnbaTvWsnriSoFAly025cC
GwwACgkQbaTvWsnriSqzewD+JDfQwbYmNVzshxGGHslGO9yx3WShsdQUxZgs4HeD
qd4BAMRseQ8Lg7Np6xDdqm4m2YaNhQmebe3pnwN81514V20J
=gMOI
-----END PGP PUBLIC KEY BLOCK-----"""

test_gpg_key_fpr = '86573E2E4947559823EC3F14C7E19A981AEA8EBB'
test_gpg_key_algo = '22'
test_gpg_key_size = 256
test_gpg_key_name = 'debexpo testing'
test_gpg_key_email = 'debexpo@example.org'

gpg_data_dir = os.path.join(os.path.dirname(__file__), 'gpg')
signed_file = os.path.join(gpg_data_dir, 'debian_announcement.gpg.asc')


class TestGnuPGController(TestCase):

    def _get_gnupg(self, gpg_path='/usr/bin/gpg'):
        settings.GPG_PATH = gpg_path
        # instantiate with new debexpo.gpg_path setting
        gnupg = GnuPG()
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

        self.assertRaises(ExceptionGnuPGPathNotInitialized, gnupg.verify_sig,
                          signed_file)
        self.assertRaises(ExceptionGnuPGPathNotInitialized, gnupg.get_keys_data)
        self.assertRaises(ExceptionGnuPGPathNotInitialized, gnupg.import_key,
                          test_gpg_key)

    def testInvalidGPGKey(self):
        """
        Test adding a wrong key
        """
        gnupg = self._get_gnupg()
        self.assertRaises(ExceptionGnuPG, gnupg.import_key,
                          '/etc/passwd')
        try:
            gnupg.import_key('/etc/passwd')
        except ExceptionGnuPG as e:
            self.assertIn('no valid OpenPGP data found', str(e))

    def testParseKeyID(self):
        """
        Test the extraction of key id from a given GPG key.
        """
        gnupg = self._get_gnupg()
        gnupg.import_key(test_gpg_key)
        self.assertFalse(gnupg.is_unusable())
        keys = gnupg.get_keys_data()
        self.assertEqual(test_gpg_key_fpr,
                         keys[0].fpr)
        self.assertIn((test_gpg_key_name, test_gpg_key_email),
                      keys[0].get_all_uid())

    def testSignatureVerification(self):
        """
        Verify the signature in the file
        debexpo/tests/gpg/debian_announcement.gpg.asc.
        """
        gnupg = self._get_gnupg()
        gnupg.import_key(test_gpg_key)
        self._assertGoodSignature(gnupg)

    def _assertGoodSignature(self, gnupg):
        self.assertFalse(gnupg.is_unusable())
        assert os.path.exists(signed_file)
        self.assertEquals(test_gpg_key_fpr,
                          gnupg.verify_sig(signed_file))

    def testUnknownSignatureVerification(self):
        """
        Verify the signature in the file
        debexpo/tests/gpg/debian_announcement.gpg.asc.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        assert os.path.exists(signed_file)
        self.assertRaises(ExceptionGnuPGNoPubKey, gnupg.verify_sig,
                          signed_file)
        try:
            gnupg.verify_sig(signed_file)
        except ExceptionGnuPGNoPubKey as e:
            self.assertEquals(e.fingerprint, test_gpg_key_fpr)
            self.assertIn(os.path.basename(signed_file), str(e))

    def testInvalidSignature(self):
        """
        Test that verify_sig() fails for an unsigned file.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        self.assertRaises(ExceptionGnuPGNotSignedFile, gnupg.verify_sig,
                          '/etc/passwd')

    def testNoFileSignature(self):
        """
        Test that verify_sig() fails for an unsigned file.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        self.assertRaises(ExceptionGnuPG, gnupg.verify_sig,
                          '/noexistent')

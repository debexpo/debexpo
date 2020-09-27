#   test_gnupg.py - Unit testing for GnuPG helpers
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Serafeim Zanikolas <serzan@hellug.gr>
#               2019 Baptiste Beauplat <lyknode@cilg.org>
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

test_gpg1_key = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBF9wZAUBCADV/3jD2YSQi3jOr2UBArlyYCdmb84Bvn4y/N/A6r7pUY6oMpXn
kh1lW3xHh7X1cilFBAKO35MqYVQFjo1K6zDj5GffcYehY4faiShzgmS16NhqlO1u
AF7kx50hTY+TVPucSpfFQ+qtyebsRFtcca/ORr3DB6Q9ssCZhhvgqhABWZqLR27D
pu2sYtsD+46BURsgO9vZFqX0EfcCi7oWlFvYSVLukGkGXa+CZ/PjNjegJASy+5KF
/g/7HibzDmv3SKBj1SVtK/EP8vnBMUNT4rIbxNbM8gk7eXIv15qRjxSfPm64I4BO
MBQgacTwe4ayZNI8Ys3zg/uHtSgO0oO/nsQ9ABEBAAG0N1Rlc3QgdXNlciAoRGVi
ZXhwbyBSU0EgdGVzdGluZyBrZXkpIDxlbWFpbEBleGFtcGxlLmNvbT6JATgEEwEI
ACIFAl9wZAUCGwMGCwkIBwMCBhUIAgkKCwQWAgMBAh4BAheAAAoJEMaeepjW8Avu
37MIAID6Iqxi7kUlcmENCa5CQMC46dBULwvGxzLHhWM7zvMBbhH5k0Ltlifm2Rgu
2Lca+6uP7tPWQcU9eyTKXNs6oK5b4iElMlsqb6hmAtQyt9gddlfe+koLbBkXbgDP
PfKvWUPqGFU/tB4jxs/Y6OUmg32YOx7wlgZIDfUqT4z+0SL0TLaVXJ9BUVBV6J1+
iOzrayHKbc3Kn8l22FIAld1q5cdFLNos6o8QIj0W9LdpzEVCK8o9RmIV2HF7aJNr
5DM1MnMNIecpE21pPMi3fx03q6bzuh+tbjAgUvXbWTh/Bt6sOVjsCuESMzYgwEk8
F/eh+mOGX5tkhuN006s6udIV+zu5AQ0EX3BkBQEIAN7Bbh/M+OsV7uuGTTg1hCdf
cUwY8qRWx/rblZxKHWkbA/lTUlL4+pGiwx6znY4acJPHkyyr8ZX8Afv+SvAEy9Yz
Dj9TBVmivJiFLOkY3FodaJvQ6IZCCkwasto6nl09w2unsZ1q3DFGtlnTwYctQCXI
w1lZHWOnfP2pOEdn8mepYtCSAvjPB+yCMlYMk0K23eeK8AM3rT1yGc33E4S3QcVG
Fd3B/6mjWoW5JV2PM/KQPs/CBzAh3puGbglsx16M8bPn4C/ynM+B2fKeGkvmR4m7
7kAwPkFTTqAINqCaqhM6FH4Mv4hwxa+nspatvN7iUtXGtxLnjv3fha50cID0cncA
EQEAAYkBHwQYAQgACQUCX3BkBQIbDAAKCRDGnnqY1vAL7npqB/9KbCAikx0LFePY
qbLyWuHnRKqXPPGCZ6WW+HzCWFKTO/rNwmaM6/Ek8OQ+FvcZSmQ49LB2VI77XKb2
R/D4jZ2vQU8YVwIyoS5LDqi3fZ9Ix3lOSBH1hs8SmIHrhkZ/wDmAAtGP6GlnQJ01
QJJRkjQKkfYGWqVRfpPCUKuPvKuXEbz3IHPLxS3GTI5JCnQeKfcbUSRDgCqIIv3L
6a5C6sT8lmTsZSTFOlMYl0Oe3S9tzWGaD3dAZCfP2+UWkW6kOQL05QS7cWS4S0FB
gp/b/eohwscTGmmnQv0b1Z0+dAJ6zKR0K3JERZC4TfNgEqayIIJflEe71/VZ6FFz
q7UsaGGA
=IhOh
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

test_gpg1_key_fpr = 'C9E825DBFFBF0E33EC5DD04CC69E7A98D6F00BEE'
test_gpg1_key_algo = '1'
test_gpg1_key_size = 2048

gpg_data_dir = os.path.join(os.path.dirname(__file__), 'gpg')
signed_file = os.path.join(gpg_data_dir, 'debian_announcement.gpg.asc')
signed_file_v1 = os.path.join(gpg_data_dir, 'debian_announcement.gpg1.asc')


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

    def testUnknownSignatureVerificationGPG1(self):
        self.testUnknownSignatureVerification(signed_file_v1, None,
                                              test_gpg1_key_fpr[-16:])

    def testUnknownSignatureVerification(self, filename=signed_file,
                                         fpr=test_gpg_key_fpr,
                                         long_id=test_gpg_key_fpr[-16:]):
        """
        Verify the signature in the file
        debexpo/tests/gpg/debian_announcement.gpg.asc.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable())
        assert os.path.exists(filename)
        self.assertRaises(ExceptionGnuPGNoPubKey, gnupg.verify_sig,
                          filename)
        try:
            gnupg.verify_sig(filename)
        except ExceptionGnuPGNoPubKey as e:
            self.assertEquals(e.fingerprint, fpr)
            self.assertEquals(e.long_id, long_id)
            self.assertIn(os.path.basename(filename), str(e))

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

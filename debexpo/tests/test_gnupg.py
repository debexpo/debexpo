# -*- coding: utf-8 -*-
#
#   utils.py — Debexpo utility functions
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
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

__author__ = 'Serafeim Zanikolas, Clément Schreiner'
__copyright__ = 'Copyright © 2008 Serafeim Zanikolas'

__license__ = 'MIT'

from unittest import TestCase
import os

import pylons.test

from debexpo.lib.gnupg import GnuPG

test_gpg_key = \
"""-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.9 (GNU/Linux)

mQGiBEMnG4URBADovsaF04fRCsE1w5IHR0YHp2+Zd1Yjd4yo16B/J9nZ5Gj6Swih
LaWhcjFL+crrP2tk6lKHXR+pYZ7pbm0jit4xAXDA2RQEvqVomps6vZVAQuZGVH57
7whF0SWrO/XJ7JH68Nk7/8gwz7ISVMlq12pzy+MTFT9216vpahI4h0rv7wCg6Y1K
RVZUp9sSFZuxJ67+ivoMfUMD/iQD8v2BznLp1XEe0rqQ3LebkGp5uuRWCPWI632e
wfI+XzNxXvqrQnn6aJ7nRsi65+bPEpz/qjKYsikSCwGMIWa6yTINutYO2ns7Ltez
y41f73vEdNm+5k4OZ4XB+zTvxoOXrWpl7MWX3O5aulGrB/vnlOTDoqTv+xoNkv2I
PwoPA/49Lr3Pm1R1rdoEBhsbnYCwBUWtUx4gEcHA45/7Gy0rmqVuCh/sqeWW4nn/
n8RfCzEDbgfxm8O5jduDkeGsem+AJJ96ERuBWiiVZ6f6rHZRwX3X5rtbGaFB0miY
48LXBwNvFBu6bcs1LSjjw1H8h5lbcJVaScl2mEn39AXmnHJKk7QlU2VyYWZlaW0g
WmFuaWtvbGFzIDxzZXJ6YW5AaGVsbHVnLmdyPohhBBMRAgAhBgsJCAcDAgMVAgMD
FgIBAh4BAheABQJIAJNBBQkMXkW8AAoJEO3CRWI1UwTk7XkAoLCRfv/kVFNq+X2Q
7E3M8cl8OAJcAKCUBbSr75DtKS9bo6Q0oeK4UkYu3YhbBBMRAgAbBgsJCAcDAgMV
AgMDFgIBAh4BAheABQJHwhWtAAoJEO3CRWI1UwTkh6MAnibtG603HMtX/fzZfsW0
hlsVwfGxAKDHyLakJZMm6n6VaLtE96T1UzIDCIhhBBMRAgAhBQJDJxuFBQkFo5qA
BgsJCAcDAgMVAgMDFgIBAh4BAheAAAoJEO3CRWI1UwTkjrwAn0+NVciUYdIhWFnj
xgCHU8XAJHGwAKDa4PJgjBMUZixcfcikoCOX4lc5WohhBBMRAgAhBgsJCAcDAgMV
AgMDFgIBAh4BAheABQJIAI9NBQkMXkHIAAoJEO3CRWI1UwTkJDUAoNX3eS0PRlIb
ZJLLvTrlQxaCgp/3AKC9Uz7oAe4Blw4C55rBgdZs9/9Gg4hGBBARAgAGBQJIE4J5
AAoJEBVYlEWZ6B2g3yMAoLjneTTHkTD758PjswGiCbfASXmVAJ95tpgA6q5Xwtj5
sn6tcv403pNOSIhGBBARAgAGBQJIC88zAAoJELdRFAn8Fdvsvq4AoJtlGCZhhRAt
V0w8/GY+tVYzY4SHAKDRGk6EzJZ4uVHypdXw/aVYD110R4hGBBARAgAGBQJIO/at
AAoJEJYs2vc7xAgfW4oAnRyYl8uRtkA+njTJb0BFnkEVToYJAKCG3wte5Y68hkoa
W4y0FEdywhObybkBDQRDJxuHEAQAjonzPvWecBu80Pte8+9J8FFoNc5THXFHhHU+
mqKNGk7bU4lCeVRM5tvMPJ/dV7+rmKgNF4MJ7MweQwQWpa0GKreB++EgijKUVtsR
95pskzJbIbwMAMnkZbMIXB/7H8VChjDH6bRtZxROpw80teQK3jE0Gw8H3Aa/ktOl
nwgfqPMAAwUD/A4y0e7CgWlCrELidCtEp/Z5DMlUJC+weUOZyknJqy3Ng9KgSD4k
1HxmF46v8YtU/BcC83ijmZzJowa/P/72WDItC5EloPHhNnu/OQ19JPEvIJlPlkAM
Y3Y26AsoHQBvZJes99XgGQYpm6N7nmJ9yoheAFIII91gVdipLAi//UuniEwEGBEC
AAwFAkMnG4cFCQWjmoAACgkQ7cJFYjVTBOS3OwCg0XRWVkOp0Fn1htlXyQO1MdAs
sS0An1yrKagH2JprS2yHBCLXdPcyAY6I
=VNMB
-----END PGP PUBLIC KEY BLOCK-----
"""

test_gpg_key_id = '1024D/355304E4'

class TestGnuPGController(TestCase):

    def _get_gnupg(self, gpg_path='/usr/bin/gpg'):
        default_keyring = pylons.test.pylonsapp.config.get('debexpo.gpg_keyring', None)
        print default_keyring
        gnupg = GnuPG(gpg_path, default_keyring)
        return gnupg

    def testGnuPGfailure1(self):
        """
        Test for debexpo.gpg_path being uninitialised.
        """
        gnupg = self._get_gnupg(None)
        self.assertTrue(gnupg.is_unusable)

    def testGnuPGfailure2(self):
        """
        Test for debexpo.gpg_path pointing to a non-existent file.
        """
        gnupg = self._get_gnupg('/non/existent')
        self.assertTrue(gnupg.is_unusable)

    def testGnuPGfailure3(self):
        """
        Test for debexpo.gpg_path pointing to a non-executable file.
        """
        gnupg = self._get_gnupg('/etc/passwd')
        self.assertTrue(gnupg.is_unusable)

    def testParseKeyID(self):
        """
        Test the extraction of key id from a given GPG key.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable)
        parsed_key_block = gnupg.parse_key_block(test_gpg_key)
        key_string = gnupg.key2string(parsed_key_block.key)
        self.assertEqual(key_string, test_gpg_key_id)

    def testSignatureVerification(self):
        """
        Verify the signature in the file
        debexpo/tests/gpg/signed_by_355304E4.gpg
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable)
        gpg_data_dir = os.path.join(os.path.dirname(__file__), 'gpg')
        signed_file = os.path.join(gpg_data_dir, 'signed_by_355304E4.gpg')
        pubring = os.path.join(gpg_data_dir, 'pubring_with_355304E4.gpg')
        assert os.path.exists(signed_file)
        assert os.path.exists(pubring)
        verif = gnupg.verify_file(path=signed_file)
        self.assertTrue(verif.is_valid)

    def testInvalidSignature(self):
        """
        Test that verify_sig() fails for an unsigned file.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable)
        verif = gnupg.verify_file(path='/etc/passwd')
        self.assertFalse(verif.is_valid)

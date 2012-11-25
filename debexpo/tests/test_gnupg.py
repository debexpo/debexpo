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

from debexpo.lib.gnupg import GnuPG, GpgUserId

clement_gpg_key = \
"""-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.19 (GNU/Linux)

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
VL17u/UK61KFOBNVOO+Jmx/cYVo75Bv1LBfIk8I=
=Vbzv
-----END PGP PUBLIC KEY BLOCK-----
"""

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
        gnupg = GnuPG(gpg_path, default_keyring)
        return gnupg

    def _get_data_file(self, name):
        gpg_data_dir = os.path.join(os.path.dirname(__file__), 'gpg')
        return os.path.join(gpg_data_dir, name)

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

    def testStringToKey(self):
        gnupg = self._get_gnupg()
        expected_key = gnupg.parse_key_block(test_gpg_key).key
        key_string = gnupg.key2string(expected_key)
        key = gnupg.string2key(key_string)
        assert key == expected_key

    def testParseUserID(self):
        """
        Test the extraction of user ids from a given GPG key.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable)
        parsed_key_block = gnupg.parse_key_block(test_gpg_key)
        (k, u) = parsed_key_block
        self.assertEqual(u, [GpgUserId('Serafeim Zanikolas',
                                       'serzan@hellug.gr')])

    def testParseInvalidKeyBlock(self):
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable)
        invalid_block = self._get_data_file('invalid_key_block')
        kb = gnupg.parse_key_block(path=invalid_block)
        assert kb.key == None

    def testAddSignature(self):
        gnupg = self._get_gnupg()
        result = gnupg.add_signature(data=test_gpg_key)
        print result.status
        self.assertTrue(result.success)

    def testObsoleteSignatureVerification(self):
        """
        Verify the signature in the file
        debexpo/tests/gpg/signed_by_355304E4.gpg.

        Since the key the file was signed with is now obsolete, the
        signature should not be valid.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable)
        signed_file = self._get_data_file('signed_by_355304E4.gpg')
        pubring = self._get_data_file('pubring_with_355304E4.gpg')

        assert os.path.exists(signed_file)
        assert os.path.exists(pubring)
        verif = gnupg.verify_file(path=signed_file)
        self.assertFalse(verif.is_valid)

    def testGoodSignature(self):
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable)
        signed_file_path = self._get_data_file('signed_by_8123F27C.gpg')
        pubring = self._get_data_file('pubring_with_8123F27C.gpg')

        assert os.path.exists(signed_file_path)
        assert os.path.exists(pubring)

        verif = gnupg.verify_file(path=signed_file_path)
        self.assertTrue(verif.is_valid)
        assert verif.data == "Lorem Ipsum is simply dummy text of the printing and typesetting industry."

    def testInvalidSignature(self):
        """
        Test that verify_sig() fails for an unsigned file.
        """
        gnupg = self._get_gnupg()
        self.assertFalse(gnupg.is_unusable)
        verif = gnupg.verify_file(path='/etc/passwd')
        self.assertFalse(verif.is_valid)

    def testRemoveSignature(self):
        gnupg = self._get_gnupg()
        result = gnupg.remove_signature('355304E4')
        print result.status
        assert result.success

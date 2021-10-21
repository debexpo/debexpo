#   test_hkp.py - Test HKP implementation
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2021 Baptiste Beauplat <lyknode@cilg.org>
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

from django.test import LiveServerTestCase

from debexpo.tools.gnupg import GnuPG

from tests import TransactionTestController


class TestHKP(TransactionTestController, LiveServerTestCase):
    def setUp(self):
        self._setup_example_user(gpg=True)

    def test_gpg_recv_keys(self):
        gpg = GnuPG()

        # On existing key
        (output, status) = gpg._run(args=[
            '--keyserver',
            'hkp://' + self.live_server_url.split('/')[2],
            '--recv-keys',
            '0x' + self._GPG_FINGERPRINT[-16:]])
        self.assertIn('IMPORT_OK 1', output)
        self.assertEquals(0, status)

        # On non-existing key
        (output, status) = gpg._run(args=[
            '--keyserver',
            'hkp://' + self.live_server_url.split('/')[2],
            '--recv-keys',
            '0xCA11AB1E'])
        self.assertIn('FAILURE recv-keys', output)
        self.assertEquals(2, status)

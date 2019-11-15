#   test_files.py - Unit testing for files helpers
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
Test cases for debexpo.tools.files
"""

from tests import TestController
from debexpo.tools.gnupg import ExceptionGnuPGNotSignedFile, \
    ExceptionGnuPG, ExceptionGnuPGNoPubKey
from debexpo.tools.files import GPGSignedFile
from debexpo.accounts.models import User
from debexpo.keyring.models import Key
from tests.unit.tools.test_gnupg import signed_file, test_gpg_key, \
        test_gpg_key_fpr, test_gpg_key_algo, test_gpg_key_size


class TestGPGSignedFileController(TestController):
    def test_invalid_file(self):
        self.assertRaises(ExceptionGnuPG, GPGSignedFile, '/noexistent')

    def test_plain_file(self):
        self.assertRaises(ExceptionGnuPGNotSignedFile, GPGSignedFile,
                          '/etc/passwd')

    def test_signed_with_unknown_key(self):
        self.assertRaises(ExceptionGnuPGNoPubKey, GPGSignedFile,
                          signed_file)

    def test_signed_file(self):
        # Setup user
        user = User.objects.create_user('debexpo@example.org',
                                        'debexpo testing', 'password')
        user.save()

        # Setup key
        self._add_gpg_key(user, test_gpg_key, test_gpg_key_fpr,
                          test_gpg_key_algo, test_gpg_key_size)

        changes = GPGSignedFile(signed_file)
        self.assertEquals(changes.get_key(), Key.objects.get(user=user))
        self.assertEquals(str(changes.get_key().algorithm), 'ed25519')

        # Remove user and key
        user.delete()

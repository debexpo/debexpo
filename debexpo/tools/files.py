#   files.py — Debexpo files handling functions
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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


from debexpo.keyring.models import Key
from debexpo.tools.gnupg import GnuPG, ExceptionGnuPGNoPubKey


class GPGSignedFile():

    def __init__(self, filename):
        # As debexpo.keyring.models also import this file, Key is imported in
        # the method scope

        self.filename = filename
        self.key = None

        fingerprint = self._lookup_fingerprint()

        try:
            self.key = Key.objects.get(fingerprint=fingerprint)
        except Key.DoesNotExist:
            raise ExceptionGnuPGNoPubKey(self.filename, fingerprint)

        self.keyring = GnuPG()
        self.keyring.import_key(self.key.key)
        self.keyring.verify_sig(self.filename)

    def _lookup_fingerprint(self):
        gpg = GnuPG()

        try:
            gpg.verify_sig(self.filename)
        except ExceptionGnuPGNoPubKey as e:
            return e.fingerprint

    def get_key(self):
        return self.key

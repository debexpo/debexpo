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

from os.path import basename
import hashlib

from debexpo.keyring.models import Key
from debexpo.tools.gnupg import GnuPG, ExceptionGnuPGNoPubKey


class ExceptionCheckSumedFile(Exception):
    pass


class ExceptionCheckSumedFileNoFile(ExceptionCheckSumedFile):
    def __init__(self, e):
        self.message = str(e)

    def __str__(self):
        return self.message


class ExceptionCheckSumedFileNoMethod(ExceptionCheckSumedFile):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f'No checksum method available for file {self.filename}.'


class ExceptionCheckSumedFileFailedSum(ExceptionCheckSumedFile):
    def __init__(self, filename, expected, computed):
        self.filename = filename
        self.expected = expected
        self.computed = computed

    def __str__(self):
        return f'Checksum failed for file {self.filename}.\n\n' \
                'Expected: {self.expected}\n' \
                'Computed: {self.computed}'


class GPGSignedFile():

    def __init__(self, filename):
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


class CheckSumedFile():
    METHODS = ('sha512', 'sha256')

    def __init__(self, filename):
        self.filename = filename
        self.checksums = {}

    def add_checksum(self, method, checksum):
        self.checksums[method] = checksum

    def validate(self):
        for method in self.METHODS:
            checksum = self.checksums.get(method)

            if checksum:
                hash_function = getattr(hashlib, method)
                validator = hash_function()

                try:
                    data = open(self.filename, 'rb')
                except IOError as e:
                    raise ExceptionCheckSumedFileNoFile(e)
                else:
                    with data:
                        while True:
                            chunk = data.read(10240)

                            if not chunk:
                                break

                            validator.update(chunk)

                if validator.hexdigest() != checksum:
                    raise ExceptionCheckSumedFileFailedSum(
                        self.filename, checksum, validator.hexdigest()
                    )
                else:
                    return True

        raise ExceptionCheckSumedFileNoMethod(self.filename)

    def __str__(self):
        return basename(self.filename)

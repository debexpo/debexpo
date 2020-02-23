#   dsc.py - Handle Dsc files
#
#   This file is part of debexpo
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

from os.path import dirname, abspath, basename
from debian import deb822
from debian.debian_support import BaseVersion

from debexpo.accounts.models import User
from debexpo.tools.files import GPGSignedFile
from debexpo.tools.debian.control import ControlFiles


class ExceptionDsc(Exception):
    pass


class Dsc(GPGSignedFile):
    def __init__(self, filename, component):
        super().__init__(abspath(filename))

        with open(self.filename, 'rb') as fd:
            self._data = deb822.Dsc(fd)

        if len(self._data) == 0:
            raise ExceptionDsc('{} could not be parsed'.format(
                basename(self.filename)))

        self.component = component
        self._build_dsc()

    def _build_dsc(self):
        self.source = self._data.get('Source')
        self.version = BaseVersion(self._data.get('Version'))
        self.files = ControlFiles(dirname(self.filename), self._data)

    def authenticate(self):
        super().authenticate()
        self.uploader = User.objects.get(key=self.key)

    def validate(self):
        # Per debian policy:
        # https://www.debian.org/doc/debian-policy/ch-controlfields.html#debian-source-control-files-dsc
        for key in [
            'Format',
            'Source',
            'Version',
            'Maintainer',
            'Standards-Version',
            'Checksums-Sha1',
            'Checksums-Sha256',
            'Files',
        ]:
            if key not in self._data:
                raise ExceptionDsc('Missing key '
                                   '{}'.format(key))

    def __str__(self):
        return basename(self.filename)

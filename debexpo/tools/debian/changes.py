#   changes.py — .changes file handling class
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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

"""
Holds *changes* file handling class.
"""

from debian import deb822
from debian.changelog import Changelog
from os.path import dirname, abspath, basename

from debexpo.accounts.models import User
from debexpo.tools.files import GPGSignedFile
from debexpo.tools.debian.control import ControlFiles


class ExceptionChanges(Exception):
    pass


class Changes(GPGSignedFile):
    """
    Helper class to parse *changes* files nicely.
    """

    def __init__(self, filename):
        """
        Object constructor. The object allows the user to specify **either**:

        #. a path to a *changes* file to parse

        ::

          a = Changes(filename='/tmp/packagename_version.changes')

        ``filename``
            Path to *changes* file to parse.
        """
        super().__init__(abspath(filename))

        with open(self.filename, 'rb') as fd:
            self._data = deb822.Changes(fd)

        if len(self._data) == 0:
            raise ExceptionChanges('Changes file {} could not be parsed'.format(
                self.filename))

        self._build_changes()

    def owns(self, filename):
        for item in self.files.files:
            if filename == str(item):
                return True

        return False

    def authenticate(self):
        super().authenticate()
        self.uploader = User.objects.get(key=self.key)

    def _build_changes(self):
        self.sources = self._data.get('Source')
        self.version = self._data.get('Version')
        self.changes = Changelog(self._data.get('Changes'))
        self.files = ControlFiles(dirname(self.filename), self._data)
        self.closes = self._data.get('Closes')

    def validate(self):
        # Per debian policy:
        # https://www.debian.org/doc/debian-policy/ch-controlfields.html#debian-changes-files-changes
        for key in ['Architecture', 'Changes', 'Checksums-Sha1',
                    'Checksums-Sha256', 'Date', 'Distribution', 'Files',
                    'Format', 'Maintainer', 'Source', 'Version']:
            if key not in self._data:
                raise ExceptionChanges('Changes file invalid. Missing key '
                                       '{}'.format(key))

    def __str__(self):
        return basename(self.filename)

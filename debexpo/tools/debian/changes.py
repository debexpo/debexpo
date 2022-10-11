#   changes.py — .changes file handling class
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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
from debian.debian_support import NativeVersion
from os.path import dirname, abspath, basename, join
from os import replace, unlink

from debexpo.bugs.models import Bug
from debexpo.accounts.models import User
from debexpo.tools.files import GPGSignedFile
from debexpo.tools.debian.control import ControlFiles
from debexpo.tools.debian.dsc import Dsc
from debexpo.tools.debian.source import Source
from debexpo.tools.clients.ftp_master import ClientFTPMasterAPI
from django.utils.translation import gettext_lazy as _


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
            raise ExceptionChanges(
                _('Changes file {filename} could not be parsed').format(
                    filename=self.filename))

        self._build_changes()

    def owns(self, filename):
        for item in self.files.files:
            if filename == str(item):
                return True

        return False

    def authenticate(self, gpg=True):
        if gpg:
            super().authenticate()
            self.uploader = User.objects.get(key=self.key)
        else:
            user = User.objects.lookup_user_from_address(self.uploader)

            if not user:
                raise ExceptionChanges(
                    'No user found for {uploader}'.format(
                        uploader=self.uploader))

            self.uploader = user

    def _build_changes(self):
        self.dsc = None
        self.bugs = None
        self.source_package = None
        self.maintainer = self._data.get('Maintainer')
        self.uploader = self._data.get('Changed-By', self.maintainer)
        self.source = self._data.get('Source')
        self.version = self._data.get('Version')
        self.distribution = self._data.get('Distribution')
        self.changes = self._data.get('Changes')
        self.files = ControlFiles(dirname(self.filename), self._data)
        self.closes = self._data.get('Closes', '')
        self.component = self.files.get_component()

        self._cleanup_changes()

    def _cleanup_changes(self):
        if self.changes:
            lines = self.changes.splitlines()
            if len(lines) > 1 and not lines[0]:
                self.changes = '\n'.join(lines[1:])

    def validate(self):
        # Per debian policy:
        # https://www.debian.org/doc/debian-policy/ch-controlfields.html#debian-changes-files-changes
        for key in ['Architecture', 'Changes', 'Checksums-Sha1',
                    'Checksums-Sha256', 'Date', 'Distribution', 'Files',
                    'Format', 'Maintainer', 'Source', 'Version']:
            if key not in self._data:
                raise ExceptionChanges(_('Changes file invalid. Missing key '
                                       '{key}').format(key=key))

    def get_bugs(self):
        if self.bugs is not None:
            return self.bugs

        if self.closes:
            self.bugs = Bug.objects.fetch_bugs(self.closes.split(' '))
        else:
            self.bugs = []

        return self.bugs

    def __str__(self):
        return basename(self.filename)

    def move(self, destdir):
        self.files.move(destdir)

        dest = join(destdir, basename(self.filename))
        replace(self.filename, dest)
        self.filename = dest

    def remove(self):
        self.files.remove()
        self.files = None

        unlink(self.filename)
        self.filename = None

        self.cleanup_source()

    def get_source(self):
        if not self.source_package:
            self.source_package = Source(self.dsc)

        return self.source_package

    def cleanup_source(self):
        if self.dsc:
            self.dsc.files.remove()

        if self.source_package:
            self.source_package.remove()

    def parse_dsc(self):
        filename = self.files.find(r'\.dsc$')

        if not filename:
            raise ExceptionChanges(_(
                'dsc is missing from changes\n'
                'Make sure you include the full source'
                ' (if you are using sbuild make sure to use the'
                ' --source option or the equivalent configuration'
                ' item; if you are using dpkg-buildpackage directly'
                ' use the default flags or -S for a source only'
                ' upload)'))

        try:
            self.dsc = Dsc(filename, self.component)
        except Exception as e:
            raise ExceptionChanges(e)

    def assert_newer(self):
        client = ClientFTPMasterAPI()
        versions = client.get_existing_versions_for(self.source,
                                                    self.distribution)

        if versions:
            # There can be multiple version for a single distribution, let's
            # validate against the maximum version.
            version = max([NativeVersion(version) for version in versions])

            if NativeVersion(self.version) <= NativeVersion(version):
                raise ExceptionChanges(_(
                    '{source} exists in the official Debian archive with '
                    'the version {version}/{distribution}. You may not '
                    'upload a lower or equal version to this one.'.format(
                        source=self.source,
                        version=version,
                        distribution=self.distribution,
                    )
                ))

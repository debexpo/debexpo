# -*- coding: utf-8 -*-
#
#   changes.py — .changes file handling class
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

from debian import deb822

from debexpo.lib.utils import parse_section

class Changes(object):
    """
    Helper class to parse *changes* files nicely.
    """

    def __init__(self, filename=None, string=None):
        """
        Object constructor. The object allows the user to specify **either**:

        #. a path to a *changes* file to parse
        #. a string with the *changes* file contents.

        ::

          a = Changes(filename='/tmp/packagename_version.changes')
          b = Changes(string='Source: packagename\\nMaintainer: ...')

        ``filename``
            Path to *changes* file to parse.

        ``string``
            *changes* file in a string to parse.
        """
        if (filename and string) or (not filename and not string):
            raise TypeError

        if filename:
            self._data = deb822.Changes(file(filename))
        else:
            self._data = deb822.Changes(string)

        if len(self._data) == 0:
            raise Exception('Changes file could not be parsed.')

    def get_files(self):
        """
        Returns a list of files in the *changes* file.
        """
        return [z['name'] for z in self._data['Files']]

    def __getitem__(self, key):
        """
        Returns the value of the rfc822 key specified.

        ``key``
            Key of data to request.
        """
        return self._data[key]

    def get(self, key, default=None):
        """
        Returns the value of the rfc822 key specified, but defaults
        to a specific value if not found in the rfc822 file.

        ``key``
            Key of data to request.

        ``default``
            Default return value if ``key`` does not exist.
        """
        return self._data.get(key, default)

    def get_component(self):
        """
        Returns the component of the package.
        """
        return parse_section(self._data['Files'][0]['section'])[0]

    def get_priority(self):
        """
        Returns the priority of the package.
        """
        return parse_section(self._data['Files'][0]['priority'])[1]

    def get_dsc(self):
        """
        Returns the name of the .dsc file.
        """
        for item in self.get_files():
            if item.endswith('.dsc'):
                return item

    def get_diff(self):
        """
        Returns the name of the .diff.gz file if there is one, otherwise None.
        """
        for item in self.get_files():
            if item.endswith('.diff.gz'):
                return item

        return None

    def get_pool_path(self):
        """
        Returns the path the changes file would be
        """
        return self._data.get_pool_path()

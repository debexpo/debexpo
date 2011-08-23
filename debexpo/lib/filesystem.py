# -*- coding: utf-8 -*-
#
#   checkfiles.py — checkfiles plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#             © 2011 Arno Töll <debian@toell.net>
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
Holds various filesystem checks and interaction methods to store source package on the disk.
"""

__author__ = 'Jonny Lamb and Arno Töll'
__copyright__ = 'Copyright © 2008 Jonny Lamb, © 2011 Arno Töll'
__license__ = 'MIT'

import logging
import os
import pylons

from debexpo.lib import constants
from debexpo.lib.utils import md5sum

from debian import deb822

log = logging.getLogger(__name__)

class CheckFiles(object):

    def test_files_present(self, changes_file):
        """
        Check whether each file listed in the changes file is present.
        """
        for filename in changes_file.get_files():
            log.debug('Looking whether %s was actually uploaded' % filename)
            if os.path.isfile(os.path.join(pylons.config['debexpo.upload.incoming'], filename)):
                log.debug('%s is present' % filename)
            else:
                log.critical('%s is not present; importing cannot continue' % filename)
                raise OSError("Missing file %s in incoming" % (filename))

        return True

    def test_md5sum(self, changes_file):
        """
        Check each file's md5sum and make sure the md5sum in the changes file is the same
        as the actual file's md5sum.
        """
        for file in changes_file['Files']:
            log.debug('Checking md5sum of %s' % file['name'])
            filename = os.path.join(pylons.config['debexpo.upload.incoming'], file['name'])
            if not os.path.isfile(filename):
                raise OSError("Missing file %s in incoming" % (file['name']))
            sum = md5sum(filename)

            if sum != file['md5sum']:
                log.critical('%s != %s' % (sum, file['md5sum']))
                raise OSError("MD5 sum mismatch in file %s: %s != %s" % (file['name'], sum, file['md5sum']))

        return True

    def find_orig_tarball(self, changes_file):
        """
        Look to see whether there is an orig tarball present, if the dsc refers to one.
        If it is present or not necessary, this returns True. Otherwise, it returns the
        name of the file required.

        ```changes_file```
            The changes file to parse for the orig.tar (note the dsc file referenced must exist)

        Returns a tuple (orig_filename, orig_filename_was_found)
        """
        dsc = deb822.Dsc(open(changes_file.get_dsc()))
        for file in dsc['Files']:
            if (file['name'].endswith('orig.tar.gz') or
                file['name'].endswith('orig.tar.bz2') or
                file['name'].endswith('orig.tar.xz')):
                if os.path.isfile(file['name']):
                    return (file['name'], True)
                else:
                    return (file['name'], False)

        return (None, False)


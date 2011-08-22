# -*- coding: utf-8 -*-
#
#   getorigtarball.py — getorigtarball plugin
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
Holds the getorigtarball plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

from debian import deb822
import logging
import os
import urllib
import re

from debexpo.lib.utils import md5sum
from debexpo.plugins import BasePlugin

import pylons

log = logging.getLogger(__name__)

class GetOrigTarballPlugin(BasePlugin):

    def test_orig_tarball(self):
        """
        Check whether there is an original tarball referenced by the dsc file, but not
        actually in the package upload.

        This procedure is skipped to avoid denial of service attacks when a package is
        larger than the configured size
        """

        # Set download of files, when the expected file size of the orig.tar.gz is larger
        # than the configured threshold.
        # XXX TODO: This size should be the 75% quartile, that is the value where 75% of all
        #           packages are smaller than that. For now, blindly assume this as 15M
        size = 15728640
        log.debug('Checking whether an orig tarball mentioned in the dsc is missing')
        dsc = deb822.Dsc(file(self.changes.get_dsc()))

        orig = None
        for dscfile in dsc['Files']:
            dscfile['size'] = int(dscfile['size'])
            if re.search('(orig\.tar\.(gz|bz2|xz))$', dscfile['name']):
                orig = dscfile
                if dscfile['size'] > size:
                        log.warning("Skipping eventual download of orig.tar.gz %s: size %d > %d" % (dscfile['name'], dscfile['size'], size))
                        return
                break

        # There is no orig.tar.gz file in the dsc file. This is probably a native package.
        if orig is None:
            log.debug('No orig.tar.gz file found; native package?')
            return

        # An orig.tar.gz was found in the dsc, and also in the upload.
        if os.path.isfile(orig['name']):
            log.debug('%s found successfully', orig['name'])
            return

        log.debug('Could not find %s; looking in Debian for it', orig['name'])

        url = os.path.join(pylons.config['debexpo.debian_mirror'], self.changes.get_pool_path(), orig['name'])
        log.debug('Trying to fetch %s' % url)
        out = urllib.urlopen(url)
        contents = out.read()

        f = open(orig['name'], "wb")
        f.write(contents)
        f.close()

        if md5sum(orig['name']) == orig['md5sum']:
            log.debug('Tarball %s taken from Debian' % orig['name'])
            self.info('tarball-taken-from-debian', None)
        else:
            log.error('Tarball %s not found in Debian' % orig['name'])
	    os.unlink(orig['name'])

plugin = GetOrigTarballPlugin

outcomes = {
    'tarball-taken-from-debian' : { 'name' : 'The original tarball has been retrieved from Debian' },
}

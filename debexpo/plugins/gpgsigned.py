# -*- coding: utf-8 -*-
#
#   gpgsigned.py — gpgsigned plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
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
Holds the gpgsigned plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging
import os

from debexpo.lib import constants
from debexpo.lib.base import *
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class GpgSignedPlugin(BasePlugin):

    def test_gpg_signed(self):
        """
        Check to make sure the changes file is GPG signed.
        """
        log.debug('Checking whether the changes file is GPG signed')

        for filename in [self.changes_file, self.changes.get_dsc()]:

            try:
                f = open(filename, 'r')
                contents = f.read()
                f.close()
            except:
                log.critical('Could not open %s; continuing' % filename)
                continue

            if contents.startswith('-----BEGIN PGP SIGNED MESSAGE-----'):
                log.debug('File %s is GPG signed' % filename)
                self.passed('gpg-signed', filename, constants.PLUGIN_SEVERITY_INFO)
            else:
                log.error('File %s is not GPG signed' % filename)
                self.failed('not-gpg-signed', filename, constants.PLUGIN_SEVERITY_ERROR)

plugin = GpgSignedPlugin

outcomes = {
    'gpg-signed' : { 'name' : 'A file is GPG signed' },
    'not-gpg-signed' : { 'name' : 'A file is not GPG signed, and it should be' },
}

# -*- coding: utf-8 -*-
#
#   diffclean.py — diffclean plugin
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
Holds the diffclean plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import commands
import logging

from debexpo.lib import constants
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class DiffCleanPlugin(BasePlugin):

    def test_diff_clean(self):
        """
        Check to make sure the diff.gz is clean.
        """
        log.debug('Checking to make sure the diff.gz is clean')

        difffile = self.changes.get_diff()

        if difffile is None:
            log.warning('Package has no diff.gz file; native package?')
            return

        diffstat = commands.getoutput('diffstat -p1 %s' % difffile)

        dirty = False
        for item in diffstat.split('\n')[:-1]:
            if not item.startswith(' debian/'):
                dirty = True
                break

        if not dirty:
            log.debug('Diff file %s is clean' % difffile)
            self.passed('diff-clean', None, constants.PLUGIN_SEVERITY_INFO)
        else:
            log.error('Diff file %s is not clean' % difffile)
            self.failed('diff-dirty', diffstat, constants.PLUGIN_SEVERITY_ERROR)

plugin = DiffCleanPlugin

outcomes = {
    'diff-clean' : { 'name' : 'The diff.gz file is clean' },
    'diff-dirty' : { 'name' : 'The diff.gz file is dirty' },
}

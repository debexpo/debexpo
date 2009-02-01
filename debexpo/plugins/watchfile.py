# -*- coding: utf-8 -*-
#
#   watchfile.py — watchfile plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonnylamb@jonnylamb.com
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
Holds the watchfile plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import commands
import logging
import os

from debexpo.lib import constants
from debexpo.lib.base import *
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class WatchFilePlugin(BasePlugin):

    def _watch_file_present(self):
        return os.path.isfile(os.path.join('extracted', 'debian', 'watch'))

    def _run_uscan(self):
        if not hasattr(self, 'status') and not hasattr(self, 'output'):
            os.chdir('extracted')
            self.status, self.output = commands.getstatusoutput('uscan --verbose --report')
            os.chdir('..')

    def _watch_file_works(self):
        self._run_uscan()
        return (self.output.find('Newest version on remote site is') != -1)

    def test_watch_file_present(self):
        """
        Check to see whether there is a watch file in the package.
        """
        log.debug('Checking to see whether there is a watch file in the package')

        if self._watch_file_present():
            log.debug('Watch file present')
            self.passed('watch-file-present', None, constants.PLUGIN_SEVERITY_INFO)
        else:
            log.warning('Watch file not present')
            self.failed('watch-file-not-present', None, constants.PLUGIN_SEVERITY_WARNING)

    def test_watch_file_works(self):
        """
        Check to see whether the watch file works.
        """
        if not self._watch_file_present(): return []
        log.debug('Checking to see whether the watch file works')

        if self._watch_file_works():
            log.debug('Watch file works')
            self.passed('watch-file-works', None, constants.PLUGIN_SEVERITY_INFO)
        else:
            log.warning('Watch file does not work')
            self.failed('watch-file-does-not-work', self.output, constants.PLUGIN_SEVERITY_WARNING)

    def test_new_upstream(self):
        """
        Check to see whether there is a new upstream version.
        """
        if not self._watch_file_present(): return []
        if not self._watch_file_works(): return []
        log.debug('Looking whether there is a new upstream version')

        if self.status == 256:
            log.debug('Package is the latest upstream version')
            self.passed('no-new-upstream-available', None, constants.PLUGIN_SEVERITY_INFO)
        else:
            log.warning('Package is not the latest upstream version')
            self.failed('new-upstream-available', self.output, constants.PLUGIN_SEVERITY_WARNING)

plugin = WatchFilePlugin

outcomes = {
    'watch-file-present' : { 'name' : 'A watch file is present' },
    'watch-file-not-present' : { 'name' : 'A watch file is not present' },
    'watch-file-works' : { 'name' : 'The watch file works' },
    'watch-file-does-not-work' : { 'name' : 'The watch file does not work' },
    'new-upstream-available' : { 'name' : 'A new upstream version is available' },
    'no-new-upstream-available' : { 'name' : 'Package is the latest upstream version' },
}

# -*- coding: utf-8 -*-
#
#   watchfile.py — watchfile plugin
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2012 Nicolas Dandrimont <Nicolas.Dandrimont@crans.org>
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
__copyright__ = ', '.join([
        'Copyright © 2008 Jonny Lamb',
        'Copyright © 2012 Nicolas Dandrimont',
        ])
__license__ = 'MIT'

import subprocess
import logging
import os

from debexpo.lib import constants
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class WatchFilePlugin(BasePlugin):

    def _watch_file_present(self):
        return os.path.isfile(os.path.join('extracted', 'debian', 'watch'))

    def _run_uscan(self):
        if not hasattr(self, 'status') and not hasattr(self, 'output'):
            os.chdir('extracted')
            call = subprocess.Popen(["uscan", "--verbose", '--report'], stdout=subprocess.PIPE)
            (self.output, _) = call.communicate()
            self.status = call.returncode
            os.chdir('..')

    def _watch_file_works(self):
        self._run_uscan()
        return (self.output.find('Newest version on remote site is') != -1)

    def test_uscan(self):
        """
        Run the watch file-related checks in the package
        """

        data = {
            "watch-file-present": False,
            }
        
        log.debug('Checking to see whether there is a watch file in the package')

        if self._watch_file_present():
            log.debug('Watch file present')
            data["watch-file-present"] = True
        else:
            log.warning('Watch file not present')
            self.failed('Watch file is not present', data, constants.PLUGIN_SEVERITY_WARNING)
            return

        if self._watch_file_works():
            log.debug('Watch file works')
            data["watch-file-works"] = True
            data["uscan-output"] = self.output
        else:
            log.warning('Watch file does not work')
            data["watch-file-works"] = False
            data["uscan-output"] = self.output
            self.failed("A watch file is present but doesn't work", data, constants.PLUGIN_SEVERITY_WARNING)
            return

        log.debug('Looking whether there is a new upstream version')

        if self.status == 1:
            log.debug('Package is the latest upstream version')
            data["latest-upstream"] = True
            self.passed('Package is the latest upstream version', data, constants.PLUGIN_SEVERITY_INFO)
        else:
            log.warning('Package is not the latest upstream version')
            data["latest-upstream"] = False
            self.failed('Package is not the latest upstream version', data, constants.PLUGIN_SEVERITY_WARNING)

plugin = WatchFilePlugin


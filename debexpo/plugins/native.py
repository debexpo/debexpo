# -*- coding: utf-8 -*-
#
#   native.py — native QA plugin
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
Holds the native plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging

from debexpo.lib import constants
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class NativePlugin(BasePlugin):

    def test_native(self):
        """
        Test to see whether the package is a native package.
        """
        log.debug('Checking whether the package is native or not')

        native = True
        for file in self.changes['Files']:
            if file['name'].endswith('.diff.gz'):
                native = False
            if file['name'].endswith('.debian.tar.gz'):
                native = False

        if native:
            # Most uploads will not be native, and especially on mentors, a native
            # package is almost probably in error.
            log.warning('Package is native')
            self.failed('is-native', None, constants.PLUGIN_SEVERITY_WARNING)
        else:
            log.debug('Package is not native')
            self.passed('is-not-native', None, constants.PLUGIN_SEVERITY_INFO)

plugin = NativePlugin

outcomes = {
    'is-native' : { 'name' : 'Package is native' },
    'is-not-native' : { 'name' : 'Package is not native' },
}

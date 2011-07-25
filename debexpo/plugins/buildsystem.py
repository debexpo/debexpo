# -*- coding: utf-8 -*-
#
#   buildsystem.py — buildsystem plugin
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
Holds the buildsystem plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import logging
from debian import deb822

from debexpo.lib import constants
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class BuildSystemPlugin(BasePlugin):

    def test_build_system(self):
        """
        Finds the build system of the package.
        """
        log.debug('Finding the package\'s build system')

        dsc = deb822.Dsc(file(self.changes.get_dsc()))

        if 'cdbs' in dsc['Build-Depends']:
            log.debug('Package uses CDBS')
            self.info('uses-cdbs', None)
        elif 'debhelper (7' in dsc['Build-Depends']:
            log.debug('Package uses debhelper 7')
            self.info('uses-dh', None)
        elif 'debhelper' in dsc['Build-Depends']:
            log.debug('Package uses straight debhelper')
            self.info('uses-debhelper', None)
        else:
            log.warning('Build system cannot be determined')
            self.fail('unknown-build-system', None, constants.PLUGIN_SEVERITY_WARNING)

plugin = BuildSystemPlugin

outcomes = {
    'uses-cdbs' : { 'name' : 'The packages uses CDBS' },
    'uses-debhelper' : { 'name' : 'The package uses straight debhelper' },
    'uses-dh' : { 'name' : 'The package uses debhelper 7' },
    'unknown-build-system' : { 'name' : 'The package\'s build system cannot be determined' },
}

# -*- coding: utf-8 -*-
#
#   lintian.py — lintian plugin
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
Holds the lintian plugin.
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

class LintianPlugin(BasePlugin):

    def test_lintian(self):
        """
        Method to run lintian on the package.
        """
        log.debug('Running lintian on the package')

        output = commands.getoutput('lintian %s' % self.changes_file)

        items = output.split('\n')

        if items and output != '':
            severity = constants.PLUGIN_SEVERITY_WARNING
            outcome = 'lintian-warnings'
            logmessage = log.warning
            for item in items:
                if item.startswith('E:'):
                    severity = constants.PLUGIN_SEVERITY_ERROR
                    outcome = 'lintian-errors'
                    logmessage = log.error
                    break

            logmessage('Package is not Lintian clean')
            self.failed(outcome, output, severity)
        else:
            log.debug('Package is Lintian clean')
            self.passed('lintian-clean', None, constants.PLUGIN_SEVERITY_INFO)

plugin = LintianPlugin

outcomes = {
    'lintian-clean' : { 'name' : 'Package is Lintian clean' },
    'lintian-warnings' : { 'name' : 'Package has Lintian warnings' },
    'lintian-errors' : { 'name' : 'Package has Lintian errors' },
}

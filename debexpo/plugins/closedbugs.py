# -*- coding: utf-8 -*-
#
#   closedbugs.py — closedbugs plugin
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
Holds the closedbugs plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging
import SOAPpy

from debexpo.lib import constants
from debexpo.lib.base import *
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class ClosedBugsPlugin(BasePlugin):

    def test_closed_bugs(self):
        """
        Check to make sure the bugs closed belong to the package.
        """
        log.debug('Checking whether the bugs closed in the package belong to the package')

        try:
            closes = self.changes['Closes']
            log.debug('Creating SOAP proxy to bugs.debian.org')
            try:
                server = SOAPpy.SOAPProxy('http://bugs.debian.org/cgi-bin/soap.cgi', 'Debbugs/SOAP')
            except:
                log.critical('An error occurred when creating the SOAP proxy')

            binary_packages = self.changes['Description'].split('\n')
            binary_packages = [t.strip() for t in binary_packages]

            for bug in self.changes['Closes'].split(' '):

                try:
                    debbug = server.get_status(int(bug.strip()))
                except:
                    log.critical('An error occured when getting the bug details; skipping')
                    continue

                name = debbug.item.value['package']

                if self._package_in_descriptions(name, binary_packages):
                    log.debug('Bug #%s belongs to this package' % bug)
                    self.passed('bug-in-package', None, constants.PLUGIN_SEVERITY_INFO)
                else:
                    log.error('Bug #%s does not belong to this package' % bug)
                    self.failed('bug-not-in-package', bug, constants.PLUGIN_SEVERITY_ERROR)

        except KeyError:
            log.debug('Package does not close any bugs')

    def _package_in_descriptions(self, name, list):
        """
        Finds out whether a binary package is in a source package by looking at the Description
        field of the changes file for the binary package name.

        ``name``
            Name of the binary package.

        ``list``
            List of Description fields split by '\n'.
        """
        for item in list:
            if item.startswith(name + ' '):
                return True

        return False

plugin = ClosedBugsPlugin

outcomes = {
    'bug-not-in-package' : { 'name' : 'A bug closed in this package doesn\'t belong to this package' },
    'bug-in-package' : { 'name' : 'A bug closed in this package belongs to this package' },
}

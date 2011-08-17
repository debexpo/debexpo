# -*- coding: utf-8 -*-
#
#   debian.py — debian plugin
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
Holds the debian plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging
import urllib
import re

from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class DebianPlugin(BasePlugin):

    def _get_qa_page(self):
        if not hasattr(self, 'qa_page'):
            self.qa_page = urllib.urlopen('http://packages.qa.debian.org/%s' % self.changes['Source'])

    def _in_debian(self):
        self._get_qa_page()
        qa_page_code = self.qa_page.getcode()
        if qa_page_code == 404:
            self.in_debian = False
        else:
            self.in_debian = True

    def test_package_in_debian(self):
        """
        Finds whether the package is in Debian.
        """
        log.debug('Testing whether the package is in Debian already')

        if not hasattr(self, 'in_debian'):
            self._in_debian()

        if self.in_debian == True:
            log.debug('Package is in Debian')
            self.info('package-is-in-debian', None)
        else:
            log.debug('Package is not in Debian')
            self.info('package-is-not-in-debian', None)

    def test_last_upload(self):
        """
        Finds the date of the last upload of the package.
        """
        if not hasattr(self, 'in_debian'):
            self._in_debian()
        if self.in_debian == False:
            return

        log.debug('Finding when the last upload of the package was')

        qa_page_lines = self.qa_page.readlines()
        for item in qa_page_lines:
            if 'Accepted' in item:
                last_change = re.search("\[(\d{4}-\d{2}-\d{2})\]", item)
                if not last_change:
                    continue
                last_change = last_change.group(1)
                log.debug('Last upload on %s' % last_change)
                self.info('last-debian-upload', 'Last upload on %s' % last_change )
                return

        log.warning('Couldn\'t find last upload date')

    def test_is_nmu(self):
        """
        Finds out whether the package is an NMU.
        """
        log.debug('Finding out whether the package is an NMU')

        if 'nmu' in self.changes['Version']:
            log.debug('Package is an NMU')
            log.info('package-is-nmu', None)
        else:
            log.debug('Package is not an NMU')

    def test_is_maintainer(self):
        """
        Tests whether the package Maintainer is the Debian Maintainer.
        """
        if not self._in_debian():
            return

        log.debug('Finding out whether the package Maintainer is the Debian Maintainer')

        # TODO

    def test_is_new_maintainer(self):
        """
        Tests whether this package version introduces a new Maintainer.
        """
        if not self._in_debian():
            return

        log.debug('Finding out whether this package version introduces a new Maintainer')

        # TODO

    def test_package_closes_wnpp(self):
        """
        Tests whether the package closes wnpp bugs.
        """
        log.debug('Finding out whether the package closes wnpp bugs')

        # TODO

    def test_itp_information(self):
        """
        Finds information about any ITPs closed.
        """
        log.debug('Finding information about any ITPs closed')

        # TODO

    def test_previous_sponsors(self):
        """
        Finds previous sponsors.
        """
        log.debug('Finding previous sponsors of the package')

        # TODO

plugin = DebianPlugin

outcomes = {
    'package-is-in-debian' : { 'name' : 'Package is in Debian' },
    'package-is-not-in-debian' : { 'name' : 'Package is not in Debian' },
    'last-debian-upload' : { 'name' : 'Date package was last uploaded to Debian' },
    'package-is-nmu' : { 'name' : 'Package is a Non-Maintainer Upload' },
}

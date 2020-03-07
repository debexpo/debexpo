# -*- coding: utf-8 -*-
#
#   debian.py — debian plugin
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
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
Holds the debian plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = ', '.join([
        'Copyright © 2008 Jonny Lamb',
        'Copyright © 2012 Nicolas Dandrimont',
        ])
__license__ = 'MIT'

import logging
import lxml.html
import urllib2
from socket import timeout

from debexpo.model import meta
from debexpo.model.users import User

from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)


class DebianPlugin(BasePlugin):

    def _in_debian(self):
        self.in_debian = False

        try:
            self.qa_page = urllib2.urlopen('https://tracker.debian.org/%s' %
                                           self.changes['Source'])
        except (urllib2.URLError, timeout) as e:
            log.error('Failed to contact tracker: {}'.format(e))
            return

        self.parsed_qa = lxml.html.fromstring(self.qa_page.read())

        if len(self._qa_xpath('//span[@class="news-title"]')) > 0:
            self.in_debian = True

    def _qa_xpath(self, query, item=None):
        """Perform the xpath query on the given item"""
        if item is None:
            item = self.parsed_qa
        return item.xpath(query)

    def _test_package_in_debian(self):
        """
        Finds whether the package is in Debian.
        """
        log.debug('Testing whether the package is in Debian already')

        if self.in_debian:
            self.outcome = "Package is already in Debian"
        else:
            self.outcome = "Package is not in Debian"

        self.data["in-debian"] = self.in_debian

    def _test_last_upload(self):
        """
        Finds the date of the last upload of the package.
        """
        log.debug('Finding when the last upload of the package was')

        news = self._qa_xpath('//span[@class="news-title"]')
        for item in news:
            if 'Accepted' in item.text:
                last_change = self._qa_xpath('../../span[@class="news-date"]',
                                             item)[0].text
                log.debug('Last upload on %s' % last_change)
                self.data["latest-upload"] = last_change
                return

        log.warning('Couldn\'t find last upload date')

    def _test_is_nmu(self):
        """
        Finds out whether the package is an NMU.
        """
        log.debug('Finding out whether the package is a NMU')

        import string

        changes = ''.join((char for char in self.changes["Changes"].lower()
                           if char in string.ascii_lowercase + '\n')) \
            .splitlines()

        self.data["nmu"] = (
            any(change.startswith('nonmaintainerupload')
                for change in changes) or
            any(change.startswith('nmu') for change in changes) or
            'nmu' in self.changes["Version"]
            )

    def _get_debian_maintainer_data(self):

        self.debian_maintainers = sorted(
                self._qa_xpath('//li[span="maintainer:"]/a/child::text()') +
                self._qa_xpath('//li[span="uploaders:"]/a/child::text()')
            )

        self.user_name = ""
        self.user_email = ""

        if self.user_id is not None:
            user = meta.session.query(User).get(self.user_id)

            if user is not None:
                self.user_name = user.name
                self.user_email = user.email

    def _test_is_debian_maintainer(self):
        """
        Tests whether the package Maintainer is the Debian Maintainer.
        """

        log.debug('Finding out whether the package Maintainer is the Debian '
                  'Maintainer')

        self.data["is-debian-maintainer"] = self.user_name in \
            self.debian_maintainers

    def _test_has_new_maintainer(self):
        """
        Tests whether this package version introduces a new Maintainer.
        """
        log.debug('Finding out whether this package version introduces a new '
                  'Maintainer')

        # TODO

    def _test_previous_sponsors(self):
        """
        Finds previous sponsors.
        """
        log.debug('Finding previous sponsors of the package')

        # TODO

    def test_qa(self):
        """Run the Debian QA tests"""

        self._in_debian()

        self.outcome = ""
        self.data = {}

        self._test_package_in_debian()
        if self.in_debian:
            self._test_last_upload()
            self._test_is_nmu()
            self._get_debian_maintainer_data()
            self._test_is_debian_maintainer()
            self._test_has_new_maintainer()
            self._test_previous_sponsors()

        self.info(self.outcome, self.data)


plugin = DebianPlugin

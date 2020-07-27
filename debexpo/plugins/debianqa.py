#   debian.py - debian plugin
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2012 Nicolas Dandrimont <Nicolas.Dandrimont@crans.org>
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from string import ascii_lowercase

from debexpo.plugins.models import BasePlugin, PluginSeverity
from debexpo.tools.clients.tracker import ClientTracker, ExceptionClientTracker
from debexpo.tools.clients import ExceptionClient


class PluginDebianQA(BasePlugin):
    @property
    def name(self):
        return 'debian-qa'

    def _test_package_in_debian(self):
        """
        Finds whether the package is in Debian.
        """
        if self.package:
            self.outcome = 'Package is already in Debian'
            self.data['last_upload'] = getattr(self.package, 'last_upload',
                                               None)
        else:
            self.outcome = 'Package is not in Debian'

    def _test_is_nmu(self, changes):
        """
        Finds out whether the package is an NMU.
        """

        lines = ''.join((char for char in changes.changes.lower()
                         if char in ascii_lowercase + '\n')) \
            .splitlines()

        self.data['nmu'] = (
            any(line.startswith('nonmaintainerupload')
                for line in lines) or
            any(line.startswith('nmu') for line in lines) or
            'nmu' in changes.version
            )

    def _test_is_debian_maintainer(self, changes):
        """
        Tests whether the package Maintainer is the Debian Maintainer.
        """

        if self.package and changes.uploader.name in self.package.maintainers:
            self.data['is_debian_maintainer'] = True
        else:
            self.data['is_debian_maintainer'] = False

    def _fetch_from_tracker(self, name):
        tracker = ClientTracker()
        package = None

        try:
            package = tracker.fetch_package(name)
        except (ExceptionClient, ExceptionClientTracker):
            pass

        return package

    def run(self, changes, source):
        """Run the Debian QA tests"""

        self.package = self._fetch_from_tracker(changes.source)

        self.outcome = ''
        self.data = {'in_debian': bool(self.package)}
        self.severity = PluginSeverity.info

        self._test_package_in_debian()

        if self.package:
            self._test_is_nmu(changes)
            self._test_is_debian_maintainer(changes)

            if self.data['nmu'] and self.data['is_debian_maintainer']:
                self.outcome = 'Changelog mention NMU but uploader is the ' \
                               'maintainer in Debian'
                self.severity = PluginSeverity.error

        self.add_result('debian-qa', self.outcome, self.data, self.severity)

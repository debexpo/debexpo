# -*- coding: utf-8 -*-
#
#   test_closedbugs.py — Plugin ClosedBugs test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2019 Baptiste BEAUPLAT'
__license__ = 'MIT'

from debexpo.tests.importer import TestImporterController
from debexpo.lib.constants import PLUGIN_SEVERITY_INFO, PLUGIN_SEVERITY_ERROR


class TestPluginClosedBugs(TestImporterController):
    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def test_closes_no_bugs(self):
        self.import_source_package('hello-no-bug')
        self.assert_importer_succeeded()
        self.assert_package_no_info('hello', 'closedbugs')

    def test_closes_invalid_bugs(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_package_severity('hello', 'closedbugs',
                                     PLUGIN_SEVERITY_ERROR)
        self.assert_package_info('hello', 'closedbugs',
                                 'Package closes bugs in a wrong way')

    def test_closes_normal_bug(self):
        self.import_source_package('hello-normal-bug')
        self.assert_importer_succeeded()
        self.assert_package_severity('hello', 'closedbugs',
                                     PLUGIN_SEVERITY_INFO)
        self.assert_package_info('hello', 'closedbugs',
                                 'Package closes bug')

    def test_closes_multi_bug(self):
        self.import_source_package('hello-multi-bug')
        self.assert_importer_succeeded()
        self.assert_package_severity('hello', 'closedbugs',
                                     PLUGIN_SEVERITY_INFO)
        self.assert_package_info('hello', 'closedbugs',
                                 'Package closes bugs')
        for bug in ('616444', '696855', '719848'):
            self.assert_package_data('hello', 'closedbugs',
                                     bug)

    def test_closes_rc_bug(self):
        self.import_source_package('hello-rc-bug')
        self.assert_importer_succeeded()
        self.assert_package_severity('hello', 'closedbugs',
                                     PLUGIN_SEVERITY_INFO)
        self.assert_package_info('hello', 'closedbugs',
                                 'Package closes a RC bug')

    def test_closes_itp_bug(self):
        self.import_source_package('hello-itp-bug')
        self.assert_importer_succeeded()
        self.assert_package_severity('hello', 'closedbugs',
                                     PLUGIN_SEVERITY_INFO)
        self.assert_package_info('hello', 'closedbugs',
                                 'Package closes a ITP bug')

    def test_closes_ita_bug(self):
        self.import_source_package('hello-ita-bug')
        self.assert_importer_succeeded()
        self.assert_package_severity('hello', 'closedbugs',
                                     PLUGIN_SEVERITY_INFO)
        self.assert_package_info('hello', 'closedbugs',
                                 'Package closes a ITA bug')

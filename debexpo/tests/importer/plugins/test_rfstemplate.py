# -*- coding: utf-8 -*-
#
#   test_license.py — Plugin License test cases
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
from debexpo.lib.constants import PLUGIN_SEVERITY_INFO


class TestPluginRFSTemplate(TestImporterController):
    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def test_dep5_license(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_package_severity('hello', 'rfstemplate',
                                     PLUGIN_SEVERITY_INFO)
        self.assert_package_data('hello', 'rfstemplate',
                                 '"upstream-license": "MIT"')
        self.assert_package_data('hello', 'rfstemplate',
                                 '"upstream-author": "Vincent TIME '
                                 '<vtime@example.org>"')

    def test_license_no_license(self):
        self.import_source_package('hello-no-license')
        self.assert_importer_succeeded()
        self.assert_package_data('hello', 'rfstemplate',
                                 '"upstream-license": "[fill in]"')

    def test_license_freeform_license(self):
        self.import_source_package('hello-freeform-license')
        self.assert_importer_succeeded()
        self.assert_package_data('hello', 'rfstemplate',
                                 '"upstream-license": "[fill in]"')

    def test_changelog(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_package_severity('hello', 'rfstemplate',
                                     PLUGIN_SEVERITY_INFO)
        self.assert_package_data('hello', 'rfstemplate',
                                 'Initial release')

#   test_controlfields.py - Plugin BuildSystem test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
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

from tests.functional.importer import TestImporterController

from debexpo.plugins.models import PluginSeverity


class TestPluginNative(TestImporterController):
    def test_controlfields_has_fields(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'control-fields', 0)
        self.assert_plugin_template(
            'hello', 'href="https://salsa.debian.org/debian/hello"')
        self.assert_plugin_template(
            'hello', 'href="https://example.org"')

    def test_controlfields_no_fields(self):
        self.import_source_package('hello-no-homepage')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'control-fields', 2)
        self.assert_plugin_severity('hello', 'control-fields',
                                    PluginSeverity.warning)
        self.assert_plugin_result('hello', 'control-fields',
                                  'No Homepage field present')
        self.assert_plugin_result('hello', 'control-fields',
                                  'No VCS field present')
        self.assert_plugin_template('hello', 'No Homepage field present')

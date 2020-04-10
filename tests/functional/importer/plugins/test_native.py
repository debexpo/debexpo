#   test_native.py - Plugin BuildSystem test cases
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
    def test_is_native(self):
        outcome = 'Package is native'
        self.import_source_package('native')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'native', 1)
        self.assert_plugin_result('hello', 'native', outcome)
        self.assert_plugin_severity('hello', 'native',
                                    PluginSeverity.warning)
        self.assert_plugin_data(
            'hello',
            'native',
            {'format': '3.0 (native)'}
        )
        self.assert_plugin_template('hello', outcome)

    def test_is_not_native(self):
        outcome = 'Package is not native'
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'native', 1)
        self.assert_plugin_result('hello', 'native', outcome)
        self.assert_plugin_severity('hello', 'native',
                                    PluginSeverity.info)
        self.assert_plugin_data(
            'hello',
            'native',
            {'format': '3.0 (quilt)'}
        )
        self.assert_plugin_template('hello', outcome)

    def test_no_format(self):
        outcome = 'Package is not native'
        self.import_source_package('no-format')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'native', 1)
        self.assert_plugin_result('hello', 'native', outcome)
        self.assert_plugin_severity('hello', 'native',
                                    PluginSeverity.info)
        self.assert_plugin_data(
            'hello',
            'native',
            {'format': '1.0 (no format file)'}
        )
        self.assert_plugin_template('hello', outcome)

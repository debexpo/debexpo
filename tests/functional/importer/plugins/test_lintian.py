#   test_lintian.py - Plugin BuildSystem test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste Beauplat <lyknode@cilg.org>
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

from os.path import dirname, join

from tests.functional.importer import TestImporterController

from debexpo.plugins.models import PluginSeverity, ExceptionPlugin
from debexpo.plugins.lintian import PluginLintian
from debexpo.tools.debian.changes import Changes


class TestPluginLintian(TestImporterController):
    def test_is_lintian_info(self):
        outcome = 'Package has lintian informational tags'
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'lintian', 1)
        data = self.assert_plugin_result('hello', 'lintian', outcome)
        self.assert_plugin_severity('hello', 'lintian',
                                    PluginSeverity.info)

        self.assert_plugin_template('hello', outcome)
        self.assert_plugin_template(
            'hello',
            'https://lintian.debian.org/tags/debian-watch-file-is-missing.html'
        )

        self.assertIn(
            '',
            data['hello source']['I-Info']['debian-watch-file-is-missing'][0]
        )

    def test_lintian_error(self):
        outcome = 'Package has lintian errors'
        self.import_source_package('lintian-error')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'lintian', 1)
        self.assert_plugin_result('hello', 'lintian', outcome)
        self.assert_plugin_severity('hello', 'lintian',
                                    PluginSeverity.error)

        self.assert_plugin_template('hello', outcome)
        self.assert_plugin_template(
            'hello',
            '<span class="lintian-E" title="Error">'
        )

    def test_lintian_fail(self):
        plugin = PluginLintian()
        changes = Changes(join(dirname(__file__), '..', 'data', 'no-orig',
                               'hello_1.0-1.dsc'))
        with self.assertRaises(ExceptionPlugin) as e:
            plugin.run(changes, None)

        self.assertIn('lintian failed to run: Non-zero status 25 from '
                      'dpkg-source',
                      str(e.exception))

    def test_lintian_timeout(self):
        plugin = PluginLintian()
        changes = Changes(join(dirname(__file__), '..', 'data', 'no-orig',
                               'hello_1.0-1.dsc'))
        with self.settings(SUBPROCESS_TIMEOUT_LINTIAN=0):
            with self.assertRaises(ExceptionPlugin) as e:
                plugin.run(changes, None)

            self.assertEqual(str(e.exception),
                             'lintian took too much time to run')

    def test_lintian_mask(self):
        outcome = 'Package has lintian informational tags'
        self.import_source_package('lintian-mask')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'lintian', 1)
        self.assert_plugin_result('hello', 'lintian', outcome)
        self.assert_plugin_severity('hello', 'lintian',
                                    PluginSeverity.info)

#   test_diffclean.py - Plugin BuildSystem test cases
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


class TestPluginDiffClean(TestImporterController):
    def test_diffclean_clean(self):
        outcome = 'The package\'s .diff.gz does not modify files' \
                  ' outside of debian/'
        self.import_package('diffclean-clean')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'diff-clean', 1)
        self.assert_plugin_result('hello', 'diff-clean', outcome)
        self.assert_plugin_severity('hello', 'diff-clean',
                                    PluginSeverity.info)
        self.assert_plugin_data(
            'hello',
            'diff-clean',
            {'modified_files': []}
        )
        self.assert_plugin_template('hello', 'diff.gz does not modify files')

    def test_diffclean_dirty(self):
        outcome = 'The package\'s .diff.gz modifies files' \
                  ' outside of debian/'
        self.import_package('diffclean-dirty')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'diff-clean', 1)
        self.assert_plugin_result('hello', 'diff-clean', outcome)
        self.assert_plugin_severity('hello', 'diff-clean',
                                    PluginSeverity.warning)
        self.assert_plugin_data(
            'hello',
            'diff-clean',
            {'modified_files': [['Makefile', '3 +++']]}
        )
        self.assert_plugin_template('hello', 'diff.gz modifies files')

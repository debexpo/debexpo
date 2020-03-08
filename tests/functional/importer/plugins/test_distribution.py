#   test_distribution.py — Plugin Distribution test cases
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


class TestPluginDistribution(TestImporterController):
    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def test_distribution_unstable(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'distribution', 0)

    def test_distribution_unreleased(self):
        outcome = 'Package uploaded for the UNRELEASED distribution'
        self.import_source_package('plugin-distribution-unreleased')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'distribution',
                                    PluginSeverity.error)
        self.assert_plugin_result_count('hello', 'distribution', 1)
        self.assert_plugin_result('hello', 'distribution', outcome)
        self.assert_plugin_template('hello', outcome)

    def test_distribution_differs(self):
        outcome = 'changes and changelog distribution differs'
        self.import_package('changes-and-changelog-distribution-differs')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'distribution',
                                    PluginSeverity.error)
        self.assert_plugin_result_count('hello', 'distribution', 1)
        self.assert_plugin_result('hello', 'distribution', outcome)
        self.assert_plugin_data(
            'hello',
            'distribution',
            {'changes': 'stable', 'changelog': 'unstable'}
        )
        self.assert_plugin_template('hello', outcome)

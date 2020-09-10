#   test_plugins.py - unit test for PluginManager
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

from tests import TestController

from debexpo.plugins.models import PluginManager, BasePlugin, PluginSeverity, \
    PluginResults


class PluginBad(BasePlugin):
    pass


class PluginGood(BasePlugin):
    @property
    def name(self):
        return 'plugin-good'

    def run(self, changes, source):
        self.add_result('good-test', 'passing')


class PluginFails(BasePlugin):
    @property
    def name(self):
        return 'plugin-fails'

    def run(self, changes, source):
        self.failed('failing')


class TestPluginManager(TestController):

    def test_plugin_manager_import_inexistent_plugin(self):
        with self.settings(IMPORTER_PLUGINS=(('debexpo.plugins.not-a-plugin',
                                              'PluginNotAPlugin'),)):
            plugins = PluginManager()
            plugins.run(None, None)

    def test_plugin_manager_import_bad_plugin(self):
        with self.settings(IMPORTER_PLUGINS=(
                ('tests.unit.importer.test_plugins',
                 'PluginBad'),)):
            plugins = PluginManager()
            plugins.run(None, None)

    def test_plugin_manager_plugin_fails(self):
        with self.settings(IMPORTER_PLUGINS=(
                ('tests.unit.importer.test_plugins',
                 'PluginFails'),)):
            plugins = PluginManager()
            plugins.run(None, None)

            self.assertTrue(plugins.results)
            self.assertEquals(plugins.results[0].plugin, 'plugin-fails')
            self.assertEquals(plugins.results[0].test, 'plugin-fails')
            self.assertEquals(plugins.results[0].outcome, 'failing')
            self.assertEquals(plugins.results[0].severity,
                              PluginSeverity.failed)

    def test_plugin_manager(self):
        with self.settings(IMPORTER_PLUGINS=(
                ('tests.unit.importer.test_plugins',
                 'PluginGood'),)):
            plugins = PluginManager()
            plugins.run(None, None)

            self.assertEquals(plugins.results[0].plugin, 'plugin-good')
            self.assertEquals(plugins.results[0].test, 'good-test')
            self.assertEquals(plugins.results[0].outcome, 'passing')
            self.assertEquals(plugins.results[0].data, None)
            self.assertEquals(plugins.results[0].severity,
                              PluginSeverity.info)


class TestPluginResults(TestController):
    def test_plugin_results_no_json(self):
        result = PluginResults()

        self.assertEquals(result.data, {})

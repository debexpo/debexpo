#   test_buildsystem.py - Plugin BuildSystem test cases
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

from tests.functional.importer import TestImporterController

from debexpo.plugins.models import PluginSeverity


class TestPluginBuildSystem(TestImporterController):
    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def test_buildsystem_cdbs(self):
        outcome = 'Package uses CDBS'
        self.import_source_package('buildsystem-cdbs')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'build-system', 1)
        self.assert_plugin_result('hello', 'build-system', outcome)
        self.assert_plugin_severity('hello', 'build-system',
                                    PluginSeverity.info)
        self.assert_plugin_data(
            'hello',
            'build-system',
            {'build_system': 'cdbs'}
        )
        self.assert_plugin_template('hello', outcome)

    def test_buildsystem_dh(self):
        outcome = 'Package uses debhelper'
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'build-system', 1)
        self.assert_plugin_result('hello', 'build-system', outcome)
        self.assert_plugin_severity('hello', 'build-system',
                                    PluginSeverity.info)
        self.assert_plugin_data(
            'hello',
            'build-system',
            {'build_system': 'debhelper', 'compat_level': 11}
        )
        self.assert_plugin_template('hello', outcome)

    def test_buildsystem_dh_compat(self):
        outcome = 'Package uses debhelper-compat'
        self.import_source_package('no-first-debhelper-compat')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'build-system', 1)
        self.assert_plugin_result('hello', 'build-system', outcome)
        self.assert_plugin_severity('hello', 'build-system',
                                    PluginSeverity.info)
        self.assert_plugin_data(
            'hello',
            'build-system',
            {'build_system': 'debhelper', 'compat_level': 12}
        )
        self.assert_plugin_template('hello', outcome)

    def test_buildsystem_unknown(self):
        outcome = 'Package uses an unknown build system'
        self.import_source_package('no-dh')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'build-system', 1)
        self.assert_plugin_result('hello', 'build-system', outcome)
        self.assert_plugin_severity('hello', 'build-system',
                                    PluginSeverity.warning)
        self.assert_plugin_data(
            'hello',
            'build-system',
            {'build_system': 'unknown'}
        )
        self.assert_plugin_template('hello', outcome)

    def test_buildsystem_dh_too_old(self):
        outcome = 'Package uses debhelper with an old compatibility level'
        self.import_source_package('old-dh')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'build-system', 1)
        self.assert_plugin_result('hello', 'build-system', outcome)
        self.assert_plugin_severity('hello', 'build-system',
                                    PluginSeverity.warning)
        self.assert_plugin_data(
            'hello',
            'build-system',
            {'build_system': 'debhelper', 'compat_level': 7}
        )
        self.assert_plugin_template('hello', outcome)

    def test_buildsystem_dh_no_compat(self):
        outcome = 'Package uses debhelper with an old compatibility level'
        self.import_source_package('dh-no-compat')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'build-system', 1)
        self.assert_plugin_result('hello', 'build-system', outcome)
        self.assert_plugin_severity('hello', 'build-system',
                                    PluginSeverity.warning)
        self.assert_plugin_data(
            'hello',
            'build-system',
            {'build_system': 'debhelper', 'compat_level': None}
        )
        self.assert_plugin_template('hello', outcome)

    def test_buildsystem_dh_compat_no_version(self):
        outcome = 'Package uses debhelper-compat ' \
            'with an old compatibility level'
        self.import_source_package('dh-compat-no-version')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'build-system', 1)
        self.assert_plugin_result('hello', 'build-system', outcome)
        self.assert_plugin_severity('hello', 'build-system',
                                    PluginSeverity.warning)
        self.assert_plugin_data(
            'hello',
            'build-system',
            {'build_system': 'debhelper', 'compat_level': None}
        )
        self.assert_plugin_template('hello', outcome)

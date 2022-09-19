#   test_rfs.py — Plugin RFS test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2020 Baptiste Beauplat <lyknode@cilg.org>
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


class TestPluginRFSTemplate(TestImporterController):
    def test_utf8_changelog(self):
        self.import_source_package('hello-utf8-changelog')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'rfs',
                                    PluginSeverity.info)
        self.assert_rfs_content('hello',
                                'Subject: RFS: hello/1.0-1 -- Test package for '
                                'debexpo')
        self.assert_rfs_content('hello',
                                'Severity: normal')

    def test_dep5_license(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'rfs',
                                    PluginSeverity.info)
        self.assert_plugin_data('hello', 'rfs', {
            'licenses': 'MIT',
            'upstream_contact': 'Vincent TIME <vtime@example.org>',
        })

    def test_license_no_license(self):
        self.import_source_package('hello-no-license')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'rfs',
                                    PluginSeverity.error)
        self.assert_plugin_data('hello', 'rfs', {
            'upstream_contact': None, 'licenses': None
        })

    def test_license_freeform_license(self):
        self.import_source_package('hello-freeform-license')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'rfs',
                                    PluginSeverity.error)
        self.assert_plugin_data('hello', 'rfs', {
            'upstream_contact': None, 'licenses': None
        })

    def test_rfs_categories(self):
        self.import_source_package('hello-rfs-categories')
        self.assert_importer_succeeded()
        self.assert_rfs_content('does-not-exist',
                                'Subject: RFS: does-not-exist/1.0-1 '
                                '[NMU] [QA] [Team] -- Test package for debexpo')
        self.assert_rfs_content('does-not-exist',
                                'Severity: wishlist')

    def test_no_vcs_browser(self):
        self.import_source_package('hello-no-vcs-browser')
        self.assert_importer_succeeded()
        self.assert_rfs_content('hello',
                                'Vcs              : [fill in')

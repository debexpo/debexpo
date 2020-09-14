#   test_maintaineremail.py - Plugin MaintainerEmail test cases
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


class TestPluginMaintainerEmail(TestImporterController):
    def test_maintaineremail_maintainer(self):
        self.import_source_package('plugin-maintaineremail-maint')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'maintainer-email',
                                    PluginSeverity.info)
        self.assert_plugin_result('hello', 'maintainer-email',
                                  '"Maintainer" email is the same as the '
                                  'uploader')
        self.assert_plugin_data(
            'hello',
            'maintainer-email',
            {'user_is_maintainer': True, 'user_email': 'email@example.com',
                'maintainer_email': 'email@example.com', 'uploader_emails': []}
        )

    def test_maintaineremail_uploader(self):
        self.import_source_package('plugin-maintaineremail-upload')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'maintainer-email',
                                    PluginSeverity.info)
        self.assert_plugin_result('hello', 'maintainer-email',
                                  'The uploader is in the package\'s '
                                  '"Uploaders" field')
        self.assert_plugin_data(
            'hello',
            'maintainer-email',
            {'user_is_maintainer': True, 'user_email': 'email@example.com',
                'maintainer_email': 'vtime@example.org', 'uploader_emails':
                ['second@example.com', 'email@example.com']}
        )

    def test_maintaineremail_nmu(self):
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'maintainer-email',
                                    PluginSeverity.warning)
        self.assert_plugin_result('hello', 'maintainer-email',
                                  'The uploader is not in the package\'s '
                                  '"Maintainer" or "Uploaders" fields')
        self.assert_plugin_data(
            'hello',
            'maintainer-email',
            {'user_is_maintainer': False, 'user_email': 'email@example.com',
                'maintainer_email': 'vtime@example.org', 'uploader_emails': []}
        )

    def test_maintaineremail_team_upload(self):
        self.import_source_package('plugin-maintaineremail-team')
        self.assert_importer_succeeded()
        self.assert_plugin_severity('hello', 'maintainer-email',
                                    PluginSeverity.info)
        self.assert_plugin_result('hello', 'maintainer-email',
                                  'The uploader is not in the package\'s '
                                  '"Maintainer" or "Uploaders" fields '
                                  '(Team upload)')
        self.assert_plugin_data(
            'hello',
            'maintainer-email',
            {'user_is_maintainer': True, 'user_email': 'email@example.com',
                'maintainer_email': 'vtime@example.org', 'uploader_emails':
                ['second@example.com']}
        )

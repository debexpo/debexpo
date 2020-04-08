#   test_watch_file.py - Plugin BuildSystem test cases
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

from http.server import BaseHTTPRequestHandler

from tests.functional.importer import TestImporterController
from tests import TestingHTTPServer

from debexpo.plugins.models import PluginSeverity


class TestPluginBuildSystem(TestImporterController):
    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def test_watch_file_no_watch(self):
        outcome = 'Watch file is not present'
        self.import_source_package('hello')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'watch-file', 1)
        self.assert_plugin_result('hello', 'watch-file', outcome)
        self.assert_plugin_severity('hello', 'watch-file',
                                    PluginSeverity.warning)
        self.assert_plugin_data(
            'hello',
            'watch-file',
            {}
        )
        self.assert_plugin_template('hello', outcome)

    def test_watch_file_invalid_watch(self):
        outcome = 'A watch file is present but doesn\'t work'
        self.import_source_package('watch-file-invalid')
        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'watch-file', 1)
        self.assert_plugin_result('hello', 'watch-file', outcome)
        self.assert_plugin_severity('hello', 'watch-file',
                                    PluginSeverity.warning)
        self.assert_in_plugin_data(
            'hello',
            'watch-file',
            {'warnings': 'Skipping the line: unknownprotocol'}
        )
        self.assert_plugin_template('hello', 'A watch file is present but')

    def test_watch_file_latest_version(self):
        outcome = 'Package is the latest upstream version'

        with TestingHTTPServer(WatchSameHTTPHandler, 36471):
            self.import_source_package('watch-file-valid')

        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'watch-file', 1)
        self.assert_plugin_result('hello', 'watch-file', outcome)
        self.assert_plugin_severity('hello', 'watch-file',
                                    PluginSeverity.info)
        self.assert_plugin_data(
            'hello',
            'watch-file',
            {
                'local': '1.0', 'upstream': '1.0',
                'url': 'http://localhost:36471/hello-1.0.tar.gz'
            }
        )
        self.assert_plugin_template('hello', outcome)

    def test_watch_file_not_latest_version(self):
        outcome = 'Newer upstream version available'

        with TestingHTTPServer(WatchNewerHTTPHandler, 36471):
            self.import_source_package('watch-file-valid')

        self.assert_importer_succeeded()
        self.assert_plugin_result_count('hello', 'watch-file', 1)
        self.assert_plugin_result('hello', 'watch-file', outcome)
        self.assert_plugin_severity('hello', 'watch-file',
                                    PluginSeverity.warning)
        self.assert_plugin_data(
            'hello',
            'watch-file',
            {
                'local': '1.0', 'upstream': '1.1',
                'url': 'http://localhost:36471/hello-1.1.tar.gz'
            }
        )
        self.assert_plugin_template('hello', outcome)


class WatchNewerHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(bytes('<a href=hello-1.1.tar.gz>hello</a>', 'UTF-8'))


class WatchSameHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(bytes('<a href=hello-1.0.tar.gz>hello</a>', 'UTF-8'))

#   test_debianqa .py - Plugin DebianQA test cases
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

from tests import TestingHTTPServer
from tests.functional.importer import TestImporterController

from debexpo.plugins.models import PluginSeverity

TEMPLATE_RESPONSE_TRACKER = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Debian Package Tracker - hello</title>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-3" id="dtracker-package-left">
                    <div class="panel" role="complementary">
                        <div class="panel-heading" role="heading">
                            general
                        </div>
                        <div class="panel-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item">
                                    <span class="list-item-key"><b>maintainer:</b></span>
                                    <a href="https://qa.debian.org/developer.php?email=sanvila%40debian.org">Santiago Vila</a>
                                    <small>
                                        (<a href="https://udd.debian.org/dmd/?sanvila%40debian.org#todo" title="UDD's Debian Maintainer Dashboard">DMD</a>)
                                    </small>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-xl-7" id="dtracker-package-center">
                    <div class="panel" role="complementary">
                        <div class="panel-heading" role="heading">
                            <div class="row">
                                <div class="col-xs-12">
                                    <a href="/pkg/hello/news/">news</a>
                                </div>
                            </div>
                        </div>
                        <div class="panel-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item">
                                    [<span class="news-date">2019-05-13</span>]
                                    <a href="/news/1039745/accepted-hello-210-2-source-into-unstable/">
                                        <span class="news-title">Accepted hello 2.10-2 (source) into unstable</span>
                                    </a>
                                    (<span class="news-creator">Santiago Vila</span>)
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
"""  # noqa: E501


class TestPluginDebianQA(TestImporterController):
    def test_debianqa_not_in_debian(self):
        outcome = 'Package is not in Debian'
        package = 'hello'
        plugin = 'debian-qa'

        with TestingHTTPServer(TrackerUnknownPackage) as httpd:
            with self.settings(TRACKER_URL=f'http://localhost:{httpd.port}'):
                self.import_source_package('hello')
        self.assert_importer_succeeded()

        self.assert_plugin_result_count(package, plugin, 1)
        self.assert_plugin_result(package, plugin, outcome)
        self.assert_plugin_severity(package, plugin, PluginSeverity.info)
        self.assert_plugin_template(package, outcome)
        self.assert_plugin_data(
            package, plugin,
            {'in_debian': False}
        )

    def test_debianqa_nmu(self):
        outcome = 'Package is already in Debian'
        package = 'hello'
        plugin = 'debian-qa'

        with TestingHTTPServer(TrackerNMUPackage) as httpd:
            with self.settings(TRACKER_URL=f'http://localhost:{httpd.port}'):
                self.import_source_package('hello-nmu')
        self.assert_importer_succeeded()

        self.assert_plugin_result_count(package, plugin, 1)
        self.assert_plugin_result(package, plugin, outcome)
        self.assert_plugin_severity(package, plugin, PluginSeverity.info)
        self.assert_plugin_template(package, outcome)
        self.assert_plugin_data(
            package, plugin,
            {'in_debian': True, 'nmu': True, 'is_debian_maintainer': False,
             'last_upload': '2019-05-13'}
        )

    def test_debianqa_nmu_but_maintainer(self):
        outcome = 'Changelog mention NMU but uploader is the maintainer in ' \
                  'Debian'
        package = 'hello'
        plugin = 'debian-qa'

        with TestingHTTPServer(TrackerOwnedPackage) as httpd:
            with self.settings(TRACKER_URL=f'http://localhost:{httpd.port}'):
                self.import_source_package('hello-nmu')
        self.assert_importer_succeeded()

        self.assert_plugin_result_count(package, plugin, 1)
        self.assert_plugin_result(package, plugin, outcome)
        self.assert_plugin_severity(package, plugin, PluginSeverity.error)
        self.assert_plugin_template(package, outcome)
        self.assert_plugin_data(
            package, plugin,
            {'in_debian': True, 'nmu': True, 'is_debian_maintainer': True,
             'last_upload': '2019-05-13'}
        )


class TrackerUnknownPackage(BaseHTTPRequestHandler):
    response = '<h1>Not Found</h1><p>The requested resource was not found on ' \
               'this server.</p>'

    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(bytes(self.response, 'UTF-8'))


class TrackerNMUPackage(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(bytes(TEMPLATE_RESPONSE_TRACKER, 'UTF-8'))


class TrackerOwnedPackage(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(bytes(TEMPLATE_RESPONSE_TRACKER.replace(
            'Santiago Vila', 'Test user'), 'UTF-8'))

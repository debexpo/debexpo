#   test_minimal_version.py - Test about minimal version accepted on mentors
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

from http.server import BaseHTTPRequestHandler

from tests import TestingHTTPServer
from tests.functional.importer import TestImporterController


class TestMinimalVersion(TestImporterController):
    def __init__(self, *args, **kwargs):
        TestImporterController.__init__(self, *args, **kwargs)

    def assert_minimal_version(self, result):
        if result:
            self.assert_importer_succeeded()
        else:
            self.assert_importer_failed()
            self.assert_email_with('You may not upload a lower or equal '
                                   'version to this one')

    def import_minimal_version(self, package, httpd=None):
        if not httpd:
            with TestingHTTPServer(MadisonAPI) as httpd:
                with self.settings(
                        FTP_MASTER_API_URL=f'http://localhost:{httpd.port}'):
                    self.import_source_package(package)
        else:
            with self.settings(
                    FTP_MASTER_API_URL=f'http://localhost:{httpd.port}'):
                self.import_source_package(package)

    def test_minimal_version_greater(self):
        self.import_minimal_version('minimal-version-greater')
        self.assert_minimal_version(True)

    def test_minimal_version_equals(self):
        self.import_minimal_version('minimal-version-equals')
        self.assert_minimal_version(False)

    def test_minimal_version_lower(self):
        self.import_minimal_version('minimal-version-lower')
        self.assert_minimal_version(False)

    def test_minimal_version_new(self):
        with TestingHTTPServer(MadisonAPINoMatch) as httpd:
            self.import_minimal_version('minimal-version-lower', httpd)
        self.assert_minimal_version(True)

    def test_minimal_version_fail(self):
        with TestingHTTPServer(MadisonAPIError) as httpd:
            self.import_minimal_version('minimal-version-lower', httpd)
        self.assert_minimal_version(True)

    def test_minimal_version_fail_emtpy(self):
        with TestingHTTPServer(MadisonAPIEmpty) as httpd:
            self.import_minimal_version('minimal-version-lower', httpd)
        self.assert_minimal_version(True)

    def test_minimal_version_multiples(self):
        with TestingHTTPServer(MadisonAPIMultiple) as httpd:
            self.import_minimal_version('minimal-version-multiples', httpd)
        self.assert_minimal_version(False)


class MadisonAPIEmpty(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(b'')


class MadisonAPINoMatch(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(b'[]')


class MadisonAPIError(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(500, 'Server Internal Error')
        self.end_headers()
        self.wfile.write(b'')


class MadisonAPI(BaseHTTPRequestHandler):
    response = """[
      {
        "hello": {
          "unstable": {
            "2.0-1": {}
          }
        }
      }
    ]
    """

    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(bytes(self.response, 'UTF-8'))


class MadisonAPIMultiple(BaseHTTPRequestHandler):
    response = """[
      {
        "hello": {
          "stable": {
            "1.0-1~deb10u1": {},
            "1.1-1~deb10u1": {}
          }
        }
      }
    ]
    """

    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(bytes(self.response, 'UTF-8'))

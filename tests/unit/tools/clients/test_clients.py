#   test_clients.py - Unit testing for HTTP clients
#
#   This file is part of debexpo -
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

import unittest
from tempfile import NamedTemporaryFile
from os import unlink

from django.test import tag

from tests import TestController
from tests.tools import test_network

from debexpo.tools.clients import ClientHTTP, ExceptionClient, ClientJsonAPI


@tag('network')
@unittest.skipIf(test_network(), 'no network: {}'.format(test_network()))
class TestClientsController(TestController):
    def test_client_content(self):
        client = ClientHTTP()
        content = client.fetch_resource('https://www.debian.org/')

        self.assertIn('The Universal Operating System', str(content))

    def test_client_api(self):
        client = ClientJsonAPI()
        content = client.fetch_json_resource(
            'https://api.ftp-master.debian.org/file_in_archive/h/hello')

        self.assertEquals(type(content), list)
        self.assertEquals(len(content), 0)

    def test_client_download(self):
        client = ClientHTTP()

        filename = NamedTemporaryFile(delete=False).name
        client.download_to_file('https://www.debian.org/', filename)

        with open(filename) as download:
            self.assertIn('The Universal Operating System', download.read())

        unlink(filename)

    def test_client_api_wrong_content(self):
        client = ClientJsonAPI()

        self.assertRaises(ExceptionClient, client.fetch_json_resource,
                          'https://www.debian.org/')

    def test_client_nx_domain(self):
        client = ClientHTTP()

        self.assertRaises(ExceptionClient, client.fetch_resource,
                          'http://nonexistent')

    def test_client_404(self):
        client = ClientHTTP()

        self.assertRaises(ExceptionClient, client.fetch_resource,
                          'https://www.debian.org/windows')

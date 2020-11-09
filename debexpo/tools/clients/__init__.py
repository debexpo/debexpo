#   __init__.py - Generic network clients
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

import json
from urllib.request import urlopen
from urllib.parse import urlencode
from tempfile import NamedTemporaryFile
from os import replace
from os.path import dirname

from django.conf import settings


class ExceptionClient(Exception):
    pass


class ExceptionClientSize(ExceptionClient):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return f'Cannot fetch resource {self.url}: too much data ' \
               f'(> {int(settings.LIMIT_SIZE_DOWNLOAD / 1024 / 1024)}MB)'


class ClientHTTP():
    def _connect(self, url):
        try:
            request = urlopen(url, timeout=30)
        except IOError as e:
            raise ExceptionClient('Failed to connect to network resource.\n'
                                  f'Url was: {url}\n\n{e}')

        size = request.info().get('Content-Length')
        if size and int(size) > settings.LIMIT_SIZE_DOWNLOAD:
            raise ExceptionClientSize(url)

        return request

    def _read(self, url, fd, size=None):
        try:
            if size:
                content = fd.read(size)
            else:
                content = fd.read()

        # Catch network interruption issues.
        # Excluded from testing since recreating those condition are complex
        except IOError as e:  # pragma: no cover
            raise ExceptionClient('Failed to connect to network resource.\n'
                                  f'Url was: {url}\n\n{e}')

        return content

    def fetch_resource(self, url, params=None):
        if params:
            url = f'{url}?{urlencode(params)}'

        request = self._connect(url)
        return self._read(url, request)

    def download_to_file(self, url, filename):
        request = self._connect(url)

        with NamedTemporaryFile(dir=dirname(filename), delete=False) \
                as tempfile:
            while True:
                chunk = self._read(url, request, 4 * 1024 * 1024)

                if not chunk:
                    break

                tempfile.write(chunk)

                if tempfile.tell() > settings.LIMIT_SIZE_DOWNLOAD:
                    raise ExceptionClientSize(url)

        replace(tempfile.name, filename)


class ClientJsonAPI(ClientHTTP):
    def fetch_json_resource(self, url, params=None):
        stream = self.fetch_resource(url, params)

        try:
            content = json.loads(stream)
        except ValueError:
            raise ExceptionClient('Failed to decode reply from json api.\n'
                                  f'Route was: {url}.\n'
                                  f'Reply was {stream}')

        return content

#   __init__.py - Generic network clients
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

import json
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from os import replace
from os.path import dirname

from django.conf import settings


class ExceptionClient(Exception):
    pass


class ClientHTTP():
    def fetch_resource(self, url):
        try:
            request = urlopen(url, timeout=30)
        except IOError as e:
            raise ExceptionClient('Failed to connect to network resource.\n'
                                  f'Url was: {url}\n\n{e}')

        size = int(request.info().get('Content-Length'))
        if size > settings.LIMIT_SIZE_DOWNLOAD:
            raise ExceptionClient('The original tarball cannot be retrieved '
                                  'from Debian: file too big (> 100MB)')

        try:
            content = request.read()

        # Catch network interruption issues.
        # Excluded from testing since recreating those condition are complex
        except IOError as e:  # pragma: no cover
            raise ExceptionClient('Failed to connect to network resource.\n'
                                  f'Url was: {url}\n\n{e}')

        return content

    def download_to_file(self, url, filename):
        content = self.fetch_resource(url)

        tempfile = NamedTemporaryFile(dir=dirname(filename), delete=False)
        tempfile.write(content)

        replace(tempfile.name, filename)


class ClientJsonAPI(ClientHTTP):
    def fetch_json_resource(self, url):
        stream = self.fetch_resource(url)

        try:
            content = json.loads(stream)
        except ValueError:
            raise ExceptionClient('Failed to decode reply from json api.\n'
                                  f'Route was: {url}.\n'
                                  f'Reply was {stream}')

        return content

#   tracker.py - Debian archive client
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

from lxml.html import fromstring
from logging import getLogger

from django.conf import settings

from debexpo.tools.clients import ClientHTTP

log = getLogger(__name__)


class ExceptionClientTracker(Exception):
    pass


class ClientTracker(ClientHTTP):
    def fetch_package(self, package):
        url = f'{settings.TRACKER_URL}/pkg/{package}'
        html = self.fetch_resource(url)
        package = TrackerPackage(html)

        return package


class TrackerPackage():
    def _parse_tracker_page(self, html):
        self.doc = fromstring(html)
        news = self.doc.xpath('//span[@class="news-title"]')

        if not len(news):
            raise ExceptionClientTracker('Package is not in Debian')

        for upload in news:
            if 'Accepted' in upload.text:
                self.last_upload = upload. \
                    xpath('../../span[@class="news-date"]')[0].text
                break

        self.maintainers = sorted(
            self.doc.xpath('//li[span="maintainer:"]/a/child::text()') +
            self.doc.xpath('//li[span="uploaders:"]/a/child::text()')
        )

    def __init__(self, html):
        self._parse_tracker_page(html)

#   test_page.py - Test browsing debexpo index page
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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

from os import environ

from django.test import TestCase
from django.test import Client

PAGES = (
    ('/', 'Welcome to '),
    ('/contact/', 'are maintaining this service'),
    ('/intro-maintainers/', 'Getting an upload to Debian'),
    ('/qa/', 'How do I build a package?'),
    ('/intro-reviewers/', 'Package reviews'),
    ('/sponsors/', 'The sponsoring process'),
    ('/sponsors/guidelines/', 'Introduction for sponsors'),
    ('/sponsors/rfs-howto/', 'Subject: RFS: hello/3.1-4'),
    ('/sponsors/rfs-howto/unknown/', 'Subject: RFS: hello/3.1-4'),
)


class TestBrowsingPage(TestCase):
    def test_debexpo_no_version(self):
        client = Client()
        path = environ['PATH']
        environ['PATH'] = ''

        try:
            response = client.get('/')
        finally:
            environ['PATH'] = path

        self.assertEquals(response.status_code, 200)
        self.assertNotIn('Version', str(response.content))

    def test_page_content(self):
        client = Client()

        for url, content in PAGES:
            response = client.get(url)
            self.assertEquals(response.status_code, 200)
            self.assertIn(content, str(response.content))
            self.assertNotIn('<a href="">', str(response.content))

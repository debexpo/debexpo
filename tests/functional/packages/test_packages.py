#   test_packages.py - functional tests for packages views
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from django.urls import reverse

from tests import TestController
from debexpo.packages.models import Package


class TestPackagesController(TestController):
    def setUp(self):
        self._setup_example_user()
        self._setup_example_package()

    def tearDown(self):
        self._remove_example_package()
        self._remove_example_user()

    def _test_feed_filter(self, key=None, value=None):
        if key is None:
            response = self.client.get(reverse('packages_feed', kwargs={
                'feed': 'feed',
            }))
        else:
            response = self.client.get(reverse('packages_search_feed', kwargs={
                'key': key,
                'value': value,
                'feed': 'feed',
            }))
        self.assertEquals(200, response.status_code)
        self.assertIn('application/rss+xml', response['Content-Type'])
        self.assertIn('<title>testpackage 1.0-1</title>', str(response.content))

        return response

    def _assert_content(self, response, *args):
        for text in args:
            self.assertIn(text, str(response.content))

    def test_index(self):
        response = self.client.get(reverse('packages'))

        self.assertEquals(200, response.status_code)
        self.assertIn('text/html', response['Content-Type'])
        self._assert_content(
            response,
            '<h2>Today</h2>',
            'testpackage',
            '1.0-1 (unstable)',
            'Test user',
            '/packages/uploader/email@example.com'
            )
        self._assert_content(
            response,
            '<h2>Today</h2>',
            'anotherpackage',
            '1.0-1 (buster)',
            'Test user',
            '/packages/uploader/email@example.com'
            )

    def test_feed_with_sponsor(self):
        package = Package.objects.get(name='testpackage')
        package.needs_sponsor = True
        package.save()

        response = self._test_feed_filter()
        self.assertIn('Uploader is currently looking for a sponsor.',
                      str(response.content))

    def test_feed_section(self):
        self._test_feed_filter('section', 'admin')

    def test_feed_uploader(self):
        self._test_feed_filter('uploader', 'email@example.com')

    def test_feed_wrong_uploader(self):
        response = self.client.get(reverse('packages_search_feed', kwargs={
            'key': 'uploader',
            'value': 'nonexistent@example.com',
            'feed': 'feed',
        }))
        self.assertEquals(200, response.status_code)
        self.assertIn('application/rss+xml', response['Content-Type'])
        self.assertNotIn('<title>testpackage 1.0-1</title>',
                         str(response.content))

    def test_feed_maintainer(self):
        self._test_feed_filter('maintainer', 'Test User <email@example.com>')

    def test_name(self):
        response = self.client.get(reverse('packages_search', kwargs={
            'key': 'name',
            'value': 'anotherpackage',
        }))
        self.assertEquals(200, response.status_code)
        self.assertIn('text/html', response['Content-Type'])
        self.assertNotIn('testpackage', str(response.content))
        self.assertIn('anotherpackage', str(response.content))

    def test_architecture(self):
        response = self.client.get(reverse('packages_search', kwargs={
            'key': 'architecture',
            'value': 'all',
        }))
        self.assertEquals(200, response.status_code)
        self.assertIn('text/html', response['Content-Type'])
        self.assertIn('testpackage', str(response.content))
        self.assertNotIn('anotherpackage', str(response.content))

    def test_section(self):
        response = self.client.get(reverse('packages_search', kwargs={
            'key': 'section',
            'value': 'admin',
        }))
        self.assertEquals(200, response.status_code)
        self.assertIn('text/html', response['Content-Type'])
        self.assertIn('testpackage', str(response.content))
        self.assertNotIn('anotherpackage', str(response.content))

    def test_uploader(self):
        response = self.client.get(reverse('packages_search', kwargs={
            'key': 'uploader',
            'value': 'nonexistant@example.com',
        }))
        self.assertEquals(200, response.status_code)
        self.assertNotIn('testpackage', str(response.content))
        self.assertNotIn('anotherpackage', str(response.content))

        response = self.client.get(reverse('packages_search', kwargs={
            'key': 'uploader',
            'value': 'email@example.com'
        }))
        self.assertEquals(200, response.status_code)
        self.assertIn('text/html', response['Content-Type'])
        self.assertIn('testpackage', str(response.content))
        self.assertIn('anotherpackage', str(response.content))

    def test_bad_keyword(self):
        response = self.client.get(reverse('packages_search', kwargs={
            'key': 'badkeyword',
            'value': 'something',
        }))
        self.assertEquals(200, response.status_code)
        self.assertIn('text/html', response['Content-Type'])
        self.assertNotIn('testpackage', str(response.content))
        self.assertNotIn('anotherpackage', str(response.content))

    def test_my(self):
        response = self.client.get(reverse('packages_my'))
        self.assertEquals(302, response.status_code)
        self.assertIn(reverse('login'), response.url)

        self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.get(reverse('packages_my'))
        self.assertEquals(200, response.status_code)
        self.assertIn('text/html', response['Content-Type'])
        self.assertIn('testpackage', str(response.content))
        self.assertIn('anotherpackage', str(response.content))

    def test_maintainer(self):
        response = self.client.get(reverse('packages_search', kwargs={
            'key': 'maintainer',
            'value': 'Test User <email@example.com>',
        }))
        self.assertEquals(200, response.status_code)
        self.assertIn('text/html', response['Content-Type'])
        self.assertIn('testpackage', str(response.content))
        self.assertNotIn('anotherpackage', str(response.content))

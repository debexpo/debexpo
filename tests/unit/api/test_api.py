#   test_api.py - Test debexpo api
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

from tests import TestController
from json import loads

from debexpo.packages.models import PackageUpload

JSON_PACKAGES = [
    {
        'id': 1,
        'in_debian': False,
        'name': 'testpackage',
        'needs_sponsor': False,
        'uploaders': ['email@example.com'],
        'versions': {'unstable': '1.0-1'}
    },
    {
        'id': 2,
        'in_debian': True,
        'name': 'anotherpackage',
        'needs_sponsor': False,
        'uploaders': ['email@example.com'],
        'versions': {'buster': '1.0-1'}
    }
]

JSON_UPLOADS = [
    {
        'id': 2,
        'changes': '',
        'closes': [],
        'component': 'non-free',
        'distribution': 'buster',
        'package': 'anotherpackage',
        'package_id': 2,
        'uploaded': '2020-09-05T15:51:47.910193Z',
        'uploader': 'email@example.com',
        'version': '1.0-1'
    },
    {
        'id': 1,
        'changes': '',
        'closes': [943216],
        'component': 'main',
        'distribution': 'unstable',
        'package': 'testpackage',
        'package_id': 1,
        'uploaded': '2020-09-05T15:51:47.899449Z',
        'uploader': 'email@example.com',
        'version': '1.0-1'
    }
]


class TestAPI(TestController):
    maxDiff = 2048

    def setUp(self):
        self._setup_example_user()
        self._setup_example_package()

        for item in JSON_UPLOADS:
            item['uploaded'] = PackageUpload.objects \
                .get(id=item['id']).uploaded.isoformat() \
                .replace('+00:00', 'Z')

    def tearDown(self):
        self._remove_example_package()
        self._remove_example_user()

    def test_api_root(self):
        # Default api root
        response = self.client.get('/api/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), {
            "packages": "http://testserver/api/packages/",
            "uploads": "http://testserver/api/uploads/",
        })

        # Unknown route
        response = self.client.get('/api/non-existent')

        self.assertEqual(response.status_code, 404)

    def test_api_package_list(self):
        # With packages
        response = self.client.get('/api/packages/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), JSON_PACKAGES)

        # Without packages
        self._remove_example_package()

        response = self.client.get('/api/packages/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), [])

    def test_api_package(self):
        # With packages
        response = self.client.get('/api/packages/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), JSON_PACKAGES[0])

        # Without packages
        response = self.client.get('/api/packages/3/')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(loads(response.content), {'detail': 'Not found.'})

    def test_api_upload_list(self):
        # With uploads
        response = self.client.get('/api/uploads/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), JSON_UPLOADS)

        # Without uploads
        self._remove_example_package()

        response = self.client.get('/api/uploads/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), [])

    def test_api_upload(self):
        # With uploads
        response = self.client.get('/api/uploads/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), JSON_UPLOADS[1])

        # Without uploads
        response = self.client.get('/api/uploads/3/')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(loads(response.content), {'detail': 'Not found.'})

    def test_api_package_upload_list(self):
        # With packages
        response = self.client.get('/api/packages/1/uploads/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), [JSON_UPLOADS[1]])

        # Without packages
        self._remove_example_package()
        response = self.client.get('/api/uploads/1/uploads/')

        self.assertEqual(response.status_code, 404)

    def test_api_package_upload(self):
        # With uploads
        response = self.client.get('/api/packages/1/uploads/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.content), JSON_UPLOADS[1])

        # Without uploads
        response = self.client.get('/api/packages/1/uploads/2/')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(loads(response.content), {'detail': 'Not found.'})

        # Without packages
        response = self.client.get('/api/packages/3/uploads/3/')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(loads(response.content), {'detail': 'Not found.'})

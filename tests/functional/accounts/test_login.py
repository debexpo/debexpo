#   test_login.py - tests for login process
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

from django.urls import reverse

from tests import TestController


class TestLoginController(TestController):
    def setUp(self):
        self._setup_example_user()

    def tearDown(self):
        self._remove_example_user()

    def test_index(self):
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)
        self.assertIn('name="username"', str(response.content))
        self.assertIn('name="password"', str(response.content))

    def test__login(self):
        response = self.client.post(reverse('login'), {
            'username': 'email@example.com',
            'password': 'wrongpassword',
            'commit': 'submit'
        })
        self.assertTrue(response.status_code, 200)
        self.assertIn('error-message', str(response.content))

        response = self.client.post(reverse('login'), self._AUTHDATA)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('profile'), response.url)
        self.assertNotIn('error-message', str(response.content))

    def test__login_path_before_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('login'), response.url)

        response = self.client.post(reverse('login'), self._AUTHDATA)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('profile'), response.url)
        self.assertNotIn('error-message', str(response.content))

    def test_logout_loggedout(self):
        response = self.client.get(reverse('logout'))
        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('index'), response.url)

    def test_logout_loggedin(self):
        response = self.client.post(reverse('login'), self._AUTHDATA)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('profile'), response.url)
        self.assertNotIn('error-message', str(response.content))

        response = self.client.get(reverse('logout'))
        self.assertEquals(response.status_code, 302)
        self.assertTrue(reverse('index'), response.url)

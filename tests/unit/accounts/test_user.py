#   test_user.py - Unit test for user model
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

from django.test import TestCase

from debexpo.accounts.models import User


class TestUser(TestCase):
    def test_create_user(self):
        user = User.objects.create_user('email@example.com', 'test user',
                                        'password')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

        self.assertEquals(user.get_full_name(), 'test user')
        self.assertEquals(user.get_short_name(), 'test user')

    def test_create_user_bad_args(self):
        self.assertRaises(ValueError, User.objects.create_user, None,
                          'test user', 'password')

        self.assertRaises(ValueError, User.objects.create_user,
                          'email@example.com', None, 'password')

        self.assertRaises(ValueError, User.objects.create_superuser,
                          'email@example.com', 'test user', 'password',
                          is_staff=False)

        self.assertRaises(ValueError, User.objects.create_superuser,
                          'email@example.com', 'test user', 'password',
                          is_superuser=False)

    def test_create_superuser(self):
        user = User.objects.create_superuser('test user', 'email@example.com',
                                             'password')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_lookup_user(self):
        for unknown_email in (None, '', 'unknown@example.org',):
            self.assertEquals(
                None,
                User.objects.lookup_user_from_address(unknown_email)
            )

        user = User.objects.create_user('email@example.com', 'test user',
                                        'password')
        self.assertEquals(
            User.objects.lookup_user_from_address('User <email@example.com>'),
            user
        )

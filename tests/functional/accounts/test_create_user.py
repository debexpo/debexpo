#   test_create_user.py - functionnal test for create_user command
#
#   This file is part of debexpo
#   https://salsa.debian.com/mentors.debian.net-team/debexpo
#
#   Copyright © 2021 Kentaro Hayashi <kenhys@xdump.org>
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

from django.core.management import call_command, CommandError

from debexpo.accounts.models import User
from debexpo.accounts.models import Profile
from tests import TestController


class TestCommandCreateUser(TestController):
    def setUp(self):
        pass

    def tearDown(self):
        self._remove_example_user()

    def test_create_no_user(self):
        with self.assertRaises(CommandError) as e:
            call_command('create_user')

        self.assertIn(('Error: the following arguments are required: '
                       'name, email, password'),
                      str(e.exception))
        self.assertEqual(User.objects.all().count(), 0)

    def test_create_name_only(self):
        with self.assertRaises(CommandError) as e:
            call_command('create_user', 'unknown')

        self.assertIn(('Error: the following arguments are required: '
                       'email, password'),
                      str(e.exception))
        self.assertEqual(User.objects.all().count(), 0)

    def test_create_no_password(self):
        with self.assertRaises(CommandError) as e:
            call_command('create_user', 'unknown', 'unknown@example.com')

        self.assertIn('Error: the following arguments are required: password',
                      str(e.exception))
        self.assertEqual(User.objects.all().count(), 0)

    def test_create_invalid_email(self):
        with self.assertRaises(CommandError) as e:
            call_command('create_user',
                         'Test user', 'INVALID', 'password')

        self.assertIn('Failed to create a new user: '
                      "{'email': ['Enter a valid email address.']}",
                      str(e.exception))
        self.assertEqual(User.objects.all().count(), 0)
        self.assertEqual(Profile.objects.all().count(), 0)

    def test_create_existing_user(self):
        self._setup_example_user()
        with self.assertRaises(CommandError) as e:
            call_command('create_user',
                         'Test user', 'email@example.com', 'password')

        self.assertIn('email@example.com: already user exists',
                      str(e.exception))
        self.assertEqual(User.objects.all().count(), 1)

    def test_create_user(self):
        call_command('create_user',
                     'Test user', 'email@example.com', 'password')
        self.assertEqual(User.objects.all().count(), 1)

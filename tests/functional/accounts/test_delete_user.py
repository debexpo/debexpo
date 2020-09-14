#   test_delete_user.py - functionnal test for delete_user command
#
#   This file is part of debexpo
#   https://salsa.debian.com/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste Beauplat <lyknode@cilg.com>
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
from debexpo.packages.models import PackageUpload
from tests import TestController


class TestCommandDeleteUser(TestController):
    def setUp(self):
        self._setup_example_user()
        self._setup_example_package()

    def tearDown(self):
        self._remove_example_user()
        self._remove_example_package()

    def test_delete_no_user(self):
        with self.assertRaises(CommandError) as e:
            call_command('delete_user')

        self.assertIn('Error: the following arguments are required: email',
                      str(e.exception))
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(PackageUpload.objects.all().count(), 2)

    def test_delete_unknown_user(self):
        with self.assertRaises(CommandError) as e:
            call_command('delete_user', 'unknown@example.com')

        self.assertIn('no such user', str(e.exception))
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(PackageUpload.objects.all().count(), 2)

    def test_delete_admin_user(self):
        user = User.objects.get(email='email@example.com')

        user.is_superuser = True
        user.save()

        with self.assertRaises(CommandError) as e:
            call_command('delete_user', 'email@example.com')

        self.assertIn('is admin', str(e.exception))
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(PackageUpload.objects.all().count(), 2)

    def test_delete_user(self):
        call_command('delete_user', 'email@example.com')

        self.assertEqual(User.objects.all().count(), 0)
        self.assertEqual(PackageUpload.objects.all().count(), 0)

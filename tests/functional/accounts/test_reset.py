# -*- coding: utf-8 -*-
#
#   test_reset - test cases for password reset
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

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2019 Baptiste BEAUPLAT'
__license__ = 'MIT'


from debexpo.tests import TestController, url
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.password_reset import PasswordReset


class TestResetController(TestController):

    def setUp(self):
        self._setup_models()
        self._setup_example_user()

    def tearDown(self):
        self._remove_example_user()

    def _generate_reset_token(self):
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()

        password_reset_data = PasswordReset.create_for_user(user)
        meta.session.add(password_reset_data)
        meta.session.commit()

        return password_reset_data.temporary_auth_key

    def _assert_reset_password(self, token, result):
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        old_password = user.password

        response = self.app.get(url(controller='password_recover',
                                    action='actually_reset_password',
                                    id=token),
                                expect_errors=True)

        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        cur_password = user.password

        if result:
            self.assertEqual(response.status_int, 200)
            self.assertNotEqual(old_password, cur_password)
        else:
            self.assertEqual(response.status_int, 404)
            self.assertEqual(old_password, cur_password)

    def test_reset_wrong_key(self):
        self._assert_reset_password('that_key_should_not_exist', False)

    def test_reset_password(self):
        token = self._generate_reset_token()
        self._assert_reset_password(token, True)

    def test_reset_password_twice(self):
        token = self._generate_reset_token()
        self._assert_reset_password(token, True)
        self._assert_reset_password(token, False)

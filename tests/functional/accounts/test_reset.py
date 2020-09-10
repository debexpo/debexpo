#   test_reset - test cases for password reset
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

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import INTERNAL_RESET_URL_TOKEN, \
    INTERNAL_RESET_SESSION_TOKEN
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from debexpo.accounts.models import User

from tests import TestController


class TestResetController(TestController):

    def setUp(self):
        self._setup_example_user()

    def tearDown(self):
        self._remove_example_user()

    def _generate_reset_token(self):
        user = User.objects.get(email='email@example.com')
        token_generator = PasswordResetTokenGenerator()
        link = token_generator.make_token(user)

        return (
            urlsafe_base64_encode(force_bytes(user.pk)),
            link
        )

    def _assert_reset_password(self, uid, token, result):
        user = User.objects.get(email='email@example.com')
        old_password = user.password

        session = self.client.session
        session[INTERNAL_RESET_SESSION_TOKEN] = token
        session.save()

        response = self.client.post(reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': INTERNAL_RESET_URL_TOKEN
        }), {
            'new_password1': 'newpass',
            'new_password2': 'newpass',
            'commit': 'submit'
        })

        user = User.objects.get(email='email@example.com')
        cur_password = user.password

        if result:
            self.assertEqual(response.status_code, 302)
            self.assertNotEqual(old_password, cur_password)
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(old_password, cur_password)

    def test_reset_wrong_key(self):
        self._assert_reset_password('that_key_should_not_exist', 'x-x', False)

    def test_reset_password(self):
        (uid, token) = self._generate_reset_token()
        self._assert_reset_password(uid, token, True)

    def test_reset_password_twice(self):
        (uid, token) = self._generate_reset_token()
        self._assert_reset_password(uid, token, True)
        self._assert_reset_password(uid, token, False)

    def test_resert_request(self):
        # Request reset form
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Password recovery', str(response.content))

        # Request reset on invalid address
        self._assert_request_reset('unknown@example.com', False)

        # Request reset on valid address
        self._assert_request_reset('email@example.com', True)

    def _assert_request_reset(self, email, result):
        response = self.client.post(reverse('password_reset'), {
            'email': email
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('password_reset_done'), response.url)

        if result:
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('clicking on the link below', mail.outbox[0].body)
            self.assertIn('accounts/reset/', mail.outbox[0].body)
        else:
            self.assertEqual(len(mail.outbox), 0)

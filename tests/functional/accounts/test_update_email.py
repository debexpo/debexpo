#   test_update_email.py - Functional tests for the profile page
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2021 Baptiste Beauplat <lyknode@debian.org>
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

import logging

from re import search, sub

from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from debexpo.accounts.models import User
from debexpo.tools.token import email_change_token_generator

from tests import TransactionTestController

log = logging.getLogger(__name__)


class TestUpdateEmail(TransactionTestController):
    def setUp(self):
        self._setup_example_user()
        self._setup_example_user(True, 'another@example.org')
        self.client.post(reverse('login'), self._AUTHDATA)

    def tearDown(self):
        self._remove_example_user()

    def _get_update_token(self, email, error=None):
        data = {
            'name': 'Test user',
            'email': email,
            'commit_account': 'submit'
        }
        submit_data = {
            'uidb64': 'a',
            'token': 'x-x',
            'email': 'a',
        }
        mail.outbox = []
        response = self.client.post(reverse('profile'), data)
        submit_url = sub(r'(/[^/]*){4}$', '',
                         reverse('email_change_confirm', kwargs=submit_data))

        self.assertEquals(response.status_code, 200)

        if error:
            self.assertIn('errorlist', str(response.content))
            self.assertIn(error, str(response.content))

            return None

        self.assertIn('Check your email', str(response.content))
        self.assertIn('Confirm your new email', str(mail.outbox[0].body))
        self.assertIn(submit_url, str(mail.outbox[0].body))

        token = search(rf'{submit_url}[^/]*/[^/]*/([^/]*)',
                       str(mail.outbox[0].body))[1]

        return token

    def _submit_token(self, token, email, invalid=False, error=None,
                      redirect=None, submit_data=None):

        if not submit_data:
            user = User.objects.get(email=self._AUTHDATA['username'])
            submit_data = {
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token,
                'email': email,
            }

        submit_url = reverse('email_change_confirm', kwargs=submit_data)
        response = self.client.get(submit_url)

        if invalid:
            self.assertIn('Invalid reset link', str(response.content))

            return

        submit_data['token'] = 'change-email'
        submit_url = reverse('email_change_confirm', kwargs=submit_data)
        complete_url = reverse('email_change_complete')

        self.assertEquals(response.status_code, 302)

        if redirect:
            self.assertTrue(str(response.url).startswith(redirect))

            return

        self.assertEquals(response.url,
                          reverse('email_change_confirm', kwargs=submit_data))

        data = {
            'commit': 'submit'
        }
        response = self.client.post(reverse('email_change_confirm',
                                            kwargs=submit_data), data)

        if error:
            self.assertEquals(response.status_code, 200)
            self.assertIn(error, str(response.content))

            return

        self.assertEquals(response.status_code, 302)
        self.assertIn(complete_url, str(response.url))

        response = self.client.get(complete_url)

        self.assertEquals(response.status_code, 200)
        self.assertIn('Email changed successfully', str(response.content))

        self.assertRaises(User.DoesNotExist,
                          User.objects.get,
                          email=self._AUTHDATA['username'])
        User.objects.get(email=email)

    def _generate_update_token(self, email):
        """
        Used to generated a token bypassing address validation. It shouldn't be
        possible to do within the app but we use it to test token submission
        thoroughly.
        """
        return email_change_token_generator.make_token(
            User.objects.get(email=self._AUTHDATA['username']), email
        )

    def _change_user_email(self, old_email, new_email):
        user = User.objects.get(email=old_email)
        user.email = new_email

        user.save()

    def test_update_email_ok(self):
        token = self._get_update_token('new@example.org')

        self._submit_token(token, 'new@example.org')

    def test_update_email_already_taken(self):
        # Test on token request
        self._get_update_token('another@example.org',
                               'this email address is already registered')

        # Test on token submission
        token = self._get_update_token('new@example.org')

        self._change_user_email('another@example.org', 'new@example.org')
        self._submit_token(token, 'new@example.org',
                           error='address already exists')

    def test_update_email_invalid_token(self):
        # On first call
        invalid_data = {
            'uidb64': 'a',
            'token': 'x-x',
            'email': 'a',
        }

        self._submit_token(None, 'new@example.org',
                           invalid=True, submit_data=invalid_data)

        # On redirect call
        user = User.objects.get(email=self._AUTHDATA['username'])
        invalid_data = {
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': 'change-email',
            'email': 'another@example.org',
        }

        self._submit_token(None, 'new@example.org',
                           invalid=True, submit_data=invalid_data)

    def test_update_email_mismatch_email(self):
        token = self._get_update_token('new@example.org')

        self._submit_token(token, 'new2@example.org', True)

    def test_update_email_invalid_email(self):
        # Test on token request
        self._get_update_token('This is not an email address',
                               'Enter a valid email address.')

        # Test on token submission
        token = self._generate_update_token('This is not an email address')

        self._submit_token(token, 'This is not an email address',
                           error='Enter a valid email address.')

    def test_update_email_no_login(self):
        # Test on token submission
        self.client.get(reverse('logout'))

        token = self._generate_update_token('new@example.org')

        self._submit_token(token, 'new@example.org',
                           redirect=reverse('login'))

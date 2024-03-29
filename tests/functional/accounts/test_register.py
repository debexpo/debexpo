#   test_register.py - tests for user registration workflow
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

from django.core import mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.test import override_settings

from debexpo.accounts.models import User, UserStatus

from tests import TestController


INFO_CONTRIBUTOR = {
    'name': 'Mr. Me',
    'commit': 'submit',
    'email': 'mr_me@example.com',
    'account_type': UserStatus.contributor.value
}

INFO_DD = {
    'name': 'Mr. Me Debian',
    'commit': 'submit',
    'email': 'mr_me@debian.org',
    'account_type': UserStatus.developer.value
}


class TestRegisterController(TestController):

    def test_maintainer_signup(self, actually_delete_it=True):
        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email=INFO_CONTRIBUTOR['email'])

        self.client.post(reverse('register'), INFO_CONTRIBUTOR)

        user = User.objects.get(email='mr_me@example.com')
        self.assertEquals(user.profile.status, UserStatus.contributor.value)

        # delete it
        if actually_delete_it:
            user.delete()
        else:
            return user

    def test_maintainer_signup_with_duplicate_email(self):
        self.test_maintainer_signup(actually_delete_it=False)

        INFO = INFO_CONTRIBUTOR.copy()
        INFO['name'] = 'Mr. Me Again'

        self.client.post(reverse('register'), INFO)

        self.assertRaises(User.DoesNotExist, User.objects.get,
                          name='Mr. Me Again')

        User.objects.get(email='mr_me@example.com').delete()

    def test_maintainer_signup_with_duplicate_name(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sign up for an account', str(response.content))

        self.test_maintainer_signup(actually_delete_it=False)

        INFO = INFO_CONTRIBUTOR.copy()
        INFO['email'] = 'mr_me_again@example.com'

        self.client.post(reverse('register'), INFO)

        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email=INFO['email'])

        User.objects.get(email=INFO_CONTRIBUTOR['email']).delete()

    def test_sponsor_signup_wrong_email(self):
        INFO = INFO_CONTRIBUTOR.copy()
        INFO['account_type'] = UserStatus.developer.value

        response = self.client.post(reverse('register'), INFO)

        self.assertEqual(response.status_code, 200)
        testtext = 'A sponsor account must be registered with your' \
                   ' @debian.org address'
        self.assertIn(testtext, str(response.content))
        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email=INFO['email'])

    def test_sponsor_signup(self):
        response = self.client.post(reverse('register'), INFO_DD)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=INFO_DD['email'])
        self.assertEquals(user.profile.status, UserStatus.developer.value)

        user.delete()

    def test_activation_wrong_key(self):
        response = self.client.get(reverse('password_reset_confirm', kwargs={
            'uidb64': 'that_key_should_not_exist',
            'token': 'x-x'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid reset link', str(response.content))

    def test_successful_activation(self):
        with self.settings(DEFAULT_BOUNCE_EMAIL='<bounce@example.org>'):
            self.test_maintainer_signup(actually_delete_it=False)

        # Test bounce address
        self.assertIn('bounce@example.org',
                      str(mail.outbox[0].from_email))

        user = User.objects.get(email='mr_me@example.com')
        token_generator = PasswordResetTokenGenerator()
        link = token_generator.make_token(user)
        response = self.client.get(reverse('password_reset_confirm', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': link,
        }))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('password_reset_confirm', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': 'set-password',
        }), str(response.url))
        user.delete()

    @override_settings(REGISTRATION_SPAM_DETECTION=True)
    def test_spam_detection(self):
        # Direct POST
        self.client.post(reverse('register'), INFO_CONTRIBUTOR)

        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email=INFO_CONTRIBUTOR['email'])

        # Too fast POST
        self.client.get(reverse('register'))
        self.client.post(reverse('register'), INFO_CONTRIBUTOR)

        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email=INFO_CONTRIBUTOR['email'])

        # Normal POST
        with self.settings(REGISTRATION_MIN_ELAPSED=0):
            self.client.get(reverse('register'))
            self.client.post(reverse('register'), INFO_CONTRIBUTOR)

        user = User.objects.get(email=INFO_CONTRIBUTOR['email'])
        user.delete()

        # Per day limit reached
        with self.settings(REGISTRATION_MIN_ELAPSED=0,
                           REGISTRATION_PER_IP=3):
            self.client.get(reverse('register'))
            self.client.post(reverse('register'), INFO_CONTRIBUTOR)

        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email=INFO_CONTRIBUTOR['email'])

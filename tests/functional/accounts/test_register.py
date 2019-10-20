#   test_register.py - tests for user registration workflow
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

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from tests import TestController


class TestRegisterController(TestController):

    def test_maintainer_signup(self, actually_delete_it=True):
        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email='mr_me@example.com')

        self.client.post(reverse('register'), {
            'name': 'Mr. Me',
            'commit': 'submit',
            'email': 'mr_me@example.com',
            'account_type': 'maintainer'
        })

        user = User.objects.get(email='mr_me@example.com')

        # delete it
        if actually_delete_it:
            user.delete()
        else:
            return user

    def test_maintainer_signup_with_duplicate_email(self):
        self.test_maintainer_signup(actually_delete_it=False)

        self.client.post(reverse('register'), {
            'name': 'Mr. Me Again',
            'commit': 'submit',
            'email': 'mr_me@example.com',
            'account_type': 'maintainer'
        })

        self.assertRaises(User.DoesNotExist, User.objects.get,
                          first_name='Mr. Me Again')

        User.objects.get(email='mr_me@example.com').delete()

    def test_maintainer_signup_with_duplicate_name(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sign up for an account', str(response.content))

        self.test_maintainer_signup(actually_delete_it=False)

        self.client.post(reverse('register'), {
            'name': 'Mr. Me',
            'commit': 'submit',
            'email': 'mr_me_again@example.com',
            'account_type': 'maintainer'
        })

        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email='mr_me_again@example.com')

        User.objects.get(email='mr_me@example.com').delete()

    def test_sponsor_signup_wrong_email(self):
        response = self.client.post(reverse('register'), {
            'name': 'Mr. Me',
            'commit': 'submit',
            'email': 'mr_me@example.com',
            'account_type': 'sponsor'
        })

        self.assertEqual(response.status_code, 200)
        testtext = '{}'.format('A sponsor account must be registered with your',
                               ' @debian.org address')
        self.assertIn(testtext, str(response.content))
        self.assertRaises(User.DoesNotExist, User.objects.get,
                          email='mr_me@example.com')

    def test_sponsor_signup(self):
        response = self.client.post(reverse('register'), {
            'name': 'Mr. Me Debian',
            'commit': 'submit',
            'email': 'mr_me@debian.org',
            'account_type': 'sponsor'
        })

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email='mr_me@debian.org')
        # TODO: Comment out when actually implemented
        # self.assertEquals(user.status, constants.USER_STATUS_DEVELOPER)

        user.delete()

    def test_activation_wrong_key(self):
        response = self.client.get(reverse('password_reset_confirm', kwargs={
            'uidb64': 'that_key_should_not_exist',
            'token': 'x-x'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid reset link', str(response.content))

    def test_successful_activation(self):
        self.test_maintainer_signup(actually_delete_it=False)
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

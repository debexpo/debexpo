#   test_token.py - Test token class
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2021 Baptiste Beauplat <lyknode@debian.org>
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

from datetime import date, timedelta

from django.utils import timezone

from tests import TestController

from debexpo.accounts.models import User
from debexpo.tools.token import email_change_token_generator as token_generator


class TestToken(TestController):
    def setUp(self):
        self._setup_example_user()

        self._today = date.today()
        token_generator._today = self._now
        self.user = User.objects.get(email='email@example.com')

    def _now(self):
        return self._today

    def _expired(self):
        return self._today - timedelta(days=999)

    def tearDown(self):
        self._remove_example_user()

    def test_make_token(self):
        # Different emails produce different tokens
        token1 = token_generator.make_token(self.user, 'new@example.org')
        token2 = token_generator.make_token(self.user, 'another@example.org')

        self.assertEquals(token1.split('-')[0], token2.split('-')[0])
        self.assertNotEquals(token1.split('-')[1], token2.split('-')[1])

        # Same email+account+time produce same token
        token2 = token_generator.make_token(self.user, 'new@example.org')

        self.assertEquals(token1, token2)

        # Different time produce different tokens
        token_generator._today = self._expired
        token2 = token_generator.make_token(self.user, 'new@example.org')

        self.assertNotEquals(token1.split('-')[0], token2.split('-')[0])
        self.assertNotEquals(token1.split('-')[1], token2.split('-')[1])

    def test_check_token(self):
        # Valid token: ok
        token = token_generator.make_token(self.user, 'new@example.org')

        self.assertTrue(token_generator.check_token(
            self.user, token, 'new@example.org'
        ))

        # Bad user: ko
        self.assertFalse(token_generator.check_token(
            None, token, 'wrong@example.org'
        ))

        # Email changed: ko
        self.assertFalse(token_generator.check_token(
            self.user, token, 'wrong@example.org'
        ))

        # Invalid token: ko
        self.assertFalse(token_generator.check_token(
            self.user, 'invalid_token', 'new@example.org'
        ))

        # user updated: ko
        self.user.last_login = timezone.now()
        self.user.save()

        self.assertFalse(token_generator.check_token(
            self.user, token, 'new@example.org'
        ))

        # Expired token: ko
        token_generator._today = self._expired
        token = token_generator.make_token(self.user, 'new@example.org')
        token_generator._today = self._now

        self.assertFalse(token_generator.check_token(
            self.user, token, 'new@example.org'
        ))

#   test_cleanupaccounts.py - functionnal test for CleanAccounts task
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from datetime import timedelta, datetime, timezone

from django.test import override_settings
from django.conf import settings

from tests import TestController
from debexpo.accounts.models import User
from debexpo.accounts.tasks import CleanupAccounts


class TestCronjobCleanupAccounts(TestController):
    def setUp(self):
        self.task = CleanupAccounts()
        self.index = 0

        # Create two regular account to make sure it is not removed
        self._create_accounts(True, activated=True)
        self._create_accounts(False, activated=True)

    def tearDown(self):
        self._remove_all_users()

    # Ask for a cleanup, but no account at all
    def test_cleanup_no_users(self):
        self.task.run()

        self._assert_account_cleaned_up()

    # Ask for a cleanup, but no account are expired
    def test_cleanup_no_expired_accounts(self):
        self._create_accounts(False)

        self.task.run()

        self._assert_account_cleaned_up()

    # Ask for a cleanup, all accounts are expired
    def test_cleanup_all_expired_accounts(self):
        self._create_accounts(True)

        self.task.run()

        self._assert_account_cleaned_up()

    # Ask for a cleanup, some account are expired
    def test_cleanup_mixed_expired_accounts(self):
        self._create_accounts(True)
        self._create_accounts(False)

        self.task.run()

        self._assert_account_cleaned_up()

    # Ask for a cleanup, using a custom expiration date
    @override_settings(REGISTRATION_EXPIRATION_DAYS=2)
    def test_cleanup_custom_expired_accounts(self):
        # Re-setup the plugin
        self.task = CleanupAccounts()

        # Edit expiration date
        self.test_cleanup_mixed_expired_accounts()
        self._assert_account_cleaned_up()

    def _create_accounts(self, expired, activated=False):
        if expired:
            creation_date = self._get_expiration_date() - timedelta(days=1)
        else:
            creation_date = self._get_expiration_date() + timedelta(days=1)

        if activated:
            password = 'password'
        else:
            password = '!password'

        self.index += 1
        user = User(name='Test expiration user',
                    email=f'test.user{self.index}@example.org',
                    password=password,
                    date_joined=creation_date)
        user.save()

    def _get_expiration_date(self):
        delta = settings.REGISTRATION_EXPIRATION_DAYS

        return datetime.now(timezone.utc) - timedelta(days=delta)

    def _get_expired_accounts(self, users):
        return users.filter(
            password__startswith='!',
            date_joined__lt=self._get_expiration_date(),
            is_active=True)

    def _assert_account_cleaned_up(self):
        users = self._get_accounts()
        users_to_cleanup = self._get_expired_accounts(users)
        users_activated = users.exclude(password__startswith='!')

        # No more expired accounts
        self.assertEquals(users_to_cleanup.count(), 0)
        # Don't touch regular accounts
        self.assertEquals(users_activated.count(), 2)

    def _get_accounts(self):
        return User.objects

    def _remove_all_users(self):
        users = self._get_accounts()

        if users.count() > 0:
            users.all().delete()

# -*- coding: utf-8 -*-
#
#   py.template - template for new .py files
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

import pylons
from datetime import timedelta, datetime

from debexpo.tests.cronjobs import TestCronjob
from debexpo.model.users import User


class TestCronjobCleanupAccounts(TestCronjob):
    def setUp(self):
        self._setup_plugin('cleanupaccounts')
        self.log.debug('Expiration date is {}'.format(
            self._get_expiration_date()))

        # Create two regular account to make sure it is not removed
        self._create_accounts(True, token=None)
        self._create_accounts(False, token=None)

    def tearDown(self):
        self._remove_all_users()

    # Ask for a cleanup, but no account at all
    def test_cleanup_no_users(self):
        self._invoke_plugin()

        self._assert_account_cleaned_up()

    # Ask for a cleanup, but no account are expired
    def test_cleanup_no_expired_accounts(self):
        self._create_accounts(False)

        self._invoke_plugin()

        self._assert_account_cleaned_up()

    # Ask for a cleanup, all accounts are expired
    def test_cleanup_all_expired_accounts(self):
        self._create_accounts(True)

        self._invoke_plugin()

        self._assert_account_cleaned_up()

    # Ask for a cleanup, some account are expired
    def test_cleanup_mixed_expired_accounts(self):
        self._create_accounts(True)
        self._create_accounts(False)

        self._invoke_plugin()

        self._assert_account_cleaned_up()

    # Ask for a cleanup, using a custom expiration date
    def test_cleanup_custom_expired_accounts(self):
        app_config = pylons.test.pylonsapp.config
        default_config = app_config['token_expiration_days']
        app_config['token_expiration_days'] = '2'

        # Re-setup the plugin
        self.plugin.setup()

        # Edit expiration date
        self.test_cleanup_mixed_expired_accounts()
        self._assert_account_cleaned_up()

        app_config['token_expiration_days'] = default_config

    def _create_accounts(self, expired, token='token'):
        if expired:
            creation_date = self._get_expiration_date() - timedelta(days=1)
        else:
            creation_date = self._get_expiration_date() + timedelta(days=1)

        if token:
            self.log.debug('Creating {} account (lastlogin is {})'.format(
                'an expired' if expired else 'an',
                creation_date))
        user = User(name='Test expiration user'.format(expired),
                    email='test.user@example.org',
                    password='password',
                    verification=token,
                    lastlogin=creation_date)
        self.db.add(user)
        self.db.commit()

    def _get_expiration_date(self):
        delta = 7

        if 'token_expiration_days' in self.config:
            delta = int(self.config['token_expiration_days'])

        return datetime.now() - timedelta(days=delta)

    def _assert_account_cleaned_up(self):
        # SQLAchemly has to work with !=/== None, so no pep8 here
        users = self._get_accounts()
        users_to_cleanup = users.filter(
            (User.lastlogin < self._get_expiration_date()) &
            (User.verification != None)) # NOQA
        users_activated = users.filter(User.verification == None) # NOQA

        # No more expired accounts
        self.assertEquals(users_to_cleanup.count(), 0)
        # Don't touch regular accounts
        self.assertEquals(users_activated.count(), 2)

    def _get_accounts(self):
        return self.db.query(User) \
            .filter(User.name == 'Test expiration user')

    def _remove_all_users(self):
        users = self._get_accounts()

        if users.count() > 0:
            users.delete()
            self.db.commit()

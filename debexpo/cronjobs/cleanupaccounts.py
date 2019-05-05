# -*- coding: utf-8 -*-
#
#   py.template - template for new .py files
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Jonny Lamb <jonny@debian.org>
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

from datetime import timedelta, datetime
from debexpo.cronjobs import BaseCronjob
from debexpo.model import meta
from debexpo.model.users import User


class CleanupAccounts(BaseCronjob):
    def setup(self):
        self.db = meta.session
        if 'token_expiration_days' in self.config:
            self.expire_in = int(self.config['token_expiration_days'])
        else:
            self.expire_in = 7

    def teardown(self):
        pass

    def invoke(self):
        accounts = self._list_account_expired()
        count = self._remove_expired_accounts(accounts)
        if count > 0:
            self.log.info('{} accounts not activated removed.'.format(count))

    def _list_account_expired(self):
        # SQLAchemly has to work with != None, so no pep8 here
        return self.db.query(User) \
            .filter(User.verification != None) \
            .filter(User.lastlogin < self._get_deadline()) # NOQA

    def _get_deadline(self):
        return datetime.now() - timedelta(days=self.expire_in)

    def _remove_expired_accounts(self, accounts):
        count = accounts.delete()
        self.db.commit()
        return count


cronjob = CleanupAccounts
schedule = timedelta(minutes=60)

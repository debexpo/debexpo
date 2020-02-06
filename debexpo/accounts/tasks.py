#   tasks.py - tasks for accounts
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
from celery.task import PeriodicTask
from logging import getLogger

from django.conf import settings

from debexpo.accounts.models import User

log = getLogger(__name__)


class CleanupAccounts(PeriodicTask):
    run_every = timedelta(minutes=settings.TASK_CLEANUPACCOUNTS_BEAT)

    def __init__(self):
        self.expire_in = int(settings.REGISTRATION_EXPIRATION_DAYS)

    def run(self):
        accounts = self._list_account_expired()
        count = accounts.count()

        if count > 0:
            accounts.delete()
            log.info('{} accounts not activated removed.'.format(count))

    def _list_account_expired(self):
        return User.objects.filter(
            password__startswith='!',
            date_joined__lt=self._get_deadline(),
            is_active=True)

    def _get_deadline(self):
        return datetime.now(timezone.utc) - timedelta(days=self.expire_in)

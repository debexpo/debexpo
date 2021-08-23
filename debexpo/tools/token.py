#   token.py - token manipulation for email validation
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


from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailChangeTokenGenerator(PasswordResetTokenGenerator):
    def make_token(self, user, email):
        return self._make_token_with_timestamp(
            user,
            self._num_days(self._today()),
            email,
        )

    def check_token(self, user, token, email):
        if not (user and token and email):
            return False

        try:
            timestamp_base36, _ = token.split("-")
            timestamp = base36_to_int(timestamp_base36)
        except ValueError:
            return False

        if not constant_time_compare(
            self._make_token_with_timestamp(user, timestamp, email),
            token
                ):
            return False

        if ((self._num_days(self._today()) - timestamp) >
                settings.EMAIL_CHANGE_TIMEOUT_DAYS):
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp, email):
        timestamp_base36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp, email),
            secret=self.secret,
        ).hexdigest()[::2]

        return f'{timestamp_base36}-{hash_string}'

    def _make_hash_value(self, user, timestamp, email):
        if not user.last_login:
            login_timestamp = ''
        else:
            login_timestamp = user.last_login.replace(microsecond=0,
                                                      tzinfo=None)

        return str(user.pk) + \
            user.password + \
            user.email + \
            email + \
            str(login_timestamp) + \
            str(timestamp)


email_change_token_generator = EmailChangeTokenGenerator()

#   set_key.py - command to assign GPG key to a user
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2021 Baptiste Beauplat <lyknode@cilg.org>
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

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from debexpo.accounts.models import User
from debexpo.keyring.models import KeyManager, Key, GPGAlgo


class Command(BaseCommand):
    help = 'Assign GPG key to a user'

    def _create_bad_key(self, key_manager, user, data):
        gpg = key_manager.import_key(data)
        key = Key()

        key.key = data
        key.fingerprint = gpg.fpr
        key.user = user
        key.size = int(gpg.get_size())

        try:
            key.algorithm = GPGAlgo.objects.get(gpg_algorithm_id=gpg.get_algo())
        except GPGAlgo.DoesNotExist:
            key.algorithm = None

        return key

    def _get_user(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f'{email}: no such user')

        return user

    def _get_key(self, keyfile):
        try:
            with open(keyfile) as fh:
                gpg = fh.read()
        except Exception as e:
            raise CommandError(f'Failed to read {keyfile}: {e}')

        return gpg

    def _remove_previous_key(self, user):
        try:
            user.key.delete()
        except Key.DoesNotExist:
            pass

    def _build_new_key(self, key_manager, user, gpg, force):
        if force:
            key = self._create_bad_key(key_manager, user, gpg)
        else:
            try:
                key = key_manager.parse_key_data(gpg)
            except Exception as e:
                raise CommandError(f'Failed to parse gpg key: {e}')

            key.user = user

        return key

    def add_arguments(self, parser):
        parser.add_argument('--force', action='count',
                            help='Skip GPG validation (size and algo)')
        parser.add_argument('email', help='Email of the user to assign the key'
                                          ' to')
        parser.add_argument('key', help='GPG key file')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        email = kwargs['email']
        keyfile = kwargs['key']
        force = kwargs['force']
        key_manager = KeyManager()

        user = self._get_user(email)
        gpg = self._get_key(keyfile)
        self._remove_previous_key(user)
        key = self._build_new_key(key_manager, user, gpg, force)

        key.save()
        key.update_subkeys()

#   users.py - commands to manage users
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste Beauplat <lyknode@cilg.org>
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

from debexpo.accounts.models import User
from debexpo.packages.tasks import remove_user_uploads


class Command(BaseCommand):
    help = 'Delete a user from debexpo'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+',
                            help='Email of the user to delete')

    def handle(self, *args, **kwargs):
        for email in kwargs['email']:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise CommandError(f'{email}: no such user')

            if user.is_superuser:
                raise CommandError(f'{email}: is admin, demote before deleting')

            remove_user_uploads(user)
            user.delete()

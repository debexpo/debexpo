#   create_users.py - commands to create user account
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2021 Kentaro Hayashi <kenhys@xdump.org>
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
from django.core.exceptions import ValidationError

from debexpo.accounts.models import User
from debexpo.accounts.models import Profile


class Command(BaseCommand):
    help = 'Create a new user for debexpo'

    def add_arguments(self, parser):
        parser.add_argument('name',
                            help='User name for new account')
        parser.add_argument('email',
                            help='Email address for new account')
        parser.add_argument('password',
                            help='Password for new account')

    def handle(self, *args, **kwargs):
        try:
            email = kwargs['email']
            User.objects.get(email=email)
            raise CommandError(f'{email}: already user exists')
        except User.DoesNotExist:
            pass

        name = kwargs['name']
        email = kwargs['email']
        password = kwargs['password']
        new_user = None
        try:
            new_user = User.objects.create_user(email, name, password)
        except ValidationError as e:
            raise CommandError(f'Failed to create a new user: {str(e)}')

        new_profile = None
        try:
            new_profile = Profile(user=new_user)
            new_profile.full_clean()
        except ValidationError as e:
            raise CommandError(f'Failed to create a new user profile: {str(e)}')
        else:
            new_profile.save()

#   forms.py - Forms for the accounts app
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

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class RegistrationForm(forms.Form):
    name = forms.CharField(label=_('Full name'), max_length=150)
    email = forms.EmailField(label=_('E-mail'), max_length=100)
    account_type = forms.ChoiceField(label=_('Account type'),
                                     initial='maintainer',
                                     widget=forms.RadioSelect,
                                     choices=[('maintainer', _('Maintainer')),
                                              ('sponsor', _('Sponsor'))])

    def _validate_sponsor_account(self, account_type, email):
        if (account_type and email and account_type == 'sponsor' and
                not email.endswith('@debian.org')):
            self.add_error('account_type', _("A sponsor account must be "
                                             "registered with your @debian.org "
                                             "address"))

    def _validate_uniqueness(self, name, email):
        if name and User.objects.filter(first_name=name):
            self.add_error('name', _('A user with this name is already '
                                     'registered on the system. If it is you, '
                                     'use that account!  Otherwise use a '
                                     'different name to register.'))

        if email and User.objects.filter(email=email):
            self.add_error('email', _('A user with this email address is '
                                      'already registered on the system'))

    def clean(self):
        email = self.cleaned_data.get('email')
        name = self.cleaned_data.get('name')
        account_type = self.cleaned_data.get('account_type')

        self._validate_sponsor_account(account_type, email)
        self._validate_uniqueness(name, email)

        return self.cleaned_data

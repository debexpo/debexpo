#   forms.py - Forms for the accounts app
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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

from datetime import timedelta, datetime
from hashlib import sha256

from django import forms
from django.contrib.auth.forms import PasswordResetForm as \
    DjangoPasswordResetForm
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.cache import cache

from debexpo.tools.email import Email

from .models import Profile, User, UserStatus
from debexpo.keyring.models import Key
from debexpo.tools.gnupg import ExceptionGnuPG


class AccountForm(forms.Form):
    name = forms.CharField(label=_('Full name'), max_length=150)
    email = forms.EmailField(label=_('E-mail'), max_length=100)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.elapsed = kwargs.pop('elapsed', None)
        self.ip = kwargs.pop('ip', None)

        super().__init__(*args, **kwargs)

    def _validate_uniqueness(self, name, email):
        if (name and User.objects.filter(name=name) and
                (not self.user or self.user.name != name)):
            self.add_error('name', _('A user with this name is already '
                                     'registered on the system. If it is you, '
                                     'use that account!  Otherwise use a '
                                     'different name to register.'))

        if (email and User.objects.filter(email=email) and
                (not self.user or self.user.email != email)):
            self.add_error('email', _('A user with this email address is '
                                      'already registered on the system'))

    def clean(self):
        email = self.cleaned_data.get('email')
        name = self.cleaned_data.get('name')

        self._validate_uniqueness(name, email)

        return self.cleaned_data


class RegistrationForm(AccountForm):
    account_type = forms.ChoiceField(label=_('Account type'),
                                     initial=UserStatus.contributor.value,
                                     widget=forms.RadioSelect,
                                     choices=[(UserStatus.contributor.value,
                                               _('Maintainer')),
                                              (UserStatus.developer.value,
                                               _('Sponsor'))])

    def _validate_sponsor_account(self, account_type, email):
        if (account_type and email and account_type ==
                str(UserStatus.developer.value) and
                not email.endswith('@debian.org')):
            self.add_error('account_type', _("A sponsor account must be "
                                             "registered with your @debian.org "
                                             "address"))

    def _detect_spammer(self):
        if not settings.REGISTRATION_SPAM_DETECTION:
            return

        ip = sha256(self.ip.encode()).hexdigest()
        key = f'registration_ip_{ip}'

        cache.add(key, 0, settings.REGISTRATION_CACHE_TIMEOUT)
        count = cache.incr(key)

        if not self.elapsed or datetime.fromisoformat(self.elapsed) > \
                (datetime.now() -
                 timedelta(seconds=settings.REGISTRATION_MIN_ELAPSED)) or \
                count > settings.REGISTRATION_PER_IP:
            raise ValidationError(_('Spam detected'))

    def clean(self):
        self.cleaned_data = super().clean()
        email = self.cleaned_data.get('email')
        account_type = self.cleaned_data.get('account_type')

        self._detect_spammer()
        self._validate_sponsor_account(account_type, email)

        return self.cleaned_data


class PasswordResetForm(DjangoPasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        email = Email('email-password-reset.html')
        email.send(_('You requested a password reset'), [to_email], **context)


class EmailChangeForm(forms.ModelForm):
    read_only = True

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['email'].disabled = True

    class Meta:
        model = User
        fields = ('email',)


class ProfileForm(forms.ModelForm):
    status = forms.ChoiceField(choices=(
        UserStatus.contributor.tuple,
        UserStatus.maintainer.tuple,
    ))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.profile.status == UserStatus.developer.value:
            self.fields['status'].choices = (
                UserStatus.developer.tuple,
            )

    class Meta:
        model = Profile
        fields = ('country', 'ircnick', 'jabber', 'language', 'status')


class GPGForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def _validate_gpg_key(self, key):
        if not key:
            return

        try:
            self.key = Key.objects.parse_key_data(key)
        except (ExceptionGnuPG, ValueError) as e:
            self.add_error('key', e)

    def _validate_uniqueness(self):
        try:
            Key.objects.exclude(user=self.user) \
                .get(fingerprint=self.key.fingerprint)
        except Key.DoesNotExist:
            pass
        else:
            self.add_error('key', 'GPG Key already in use by another account')

    def clean(self):
        self.cleaned_data = super().clean()
        key = self.cleaned_data.get('key')

        self._validate_gpg_key(key)
        if hasattr(self, 'key'):
            self._validate_uniqueness()

        return self.cleaned_data

    class Meta:
        model = Key
        fields = ('key',)
        widgets = {
            'key': forms.Textarea(attrs={'rows': 12, 'cols': 66}),
        }

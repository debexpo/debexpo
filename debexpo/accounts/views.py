#   views.py — accounts views
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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

import logging

from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import RegistrationForm, AccountForm, ProfileForm
from .models import Profile, User, UserStatus

from debexpo.tools.email import Email

log = logging.getLogger(__name__)


def _send_activate_email(request, uid, token, recipient):
    """
    Sends an activation email to the potential new user.

    ``key``
        Activation key that's already stored in the database.

    ``recipient``
        Email address to send to.
    """
    log.debug('Sending activation email')
    email = Email('email-password-creation.html')
    activate_url = request.scheme + '://' + request.site.domain + \
        reverse('password_reset_confirm', kwargs={
            'uidb64': uid, 'token': token
        })
    email.send(_('Next step: Confirm your email address'), [recipient],
               activate_url=activate_url)


def _register_submit(request, info):
    """
    Handles the form submission for a maintainer account registration.
    """
    log.info('Creating new user {} <{}> as {}'.format(
        info.get('name'), info.get('email'),
        list(UserStatus.keys())[
            list(UserStatus.values()).index(int(info.get('account_type')))
        ]
    ))

    # Debexpo use the email field as the username
    user = User.objects.create_user(info.get('email'), info.get('name'))
    user.save()
    profile = Profile(user=user, status=info.get('account_type'))
    profile.save()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    _send_activate_email(request, uid, token, user.email)

    log.debug('New user saved')
    return render(request, 'activate.html', {
        'settings': settings
    })


def _update_account(request, info):
    request.user.name = info.get('name')
    request.user.email = info.get('email')
    request.user.save()


def register(request):
    """
    Provides the form for a maintainer account registration.
    """
    # Has the form been submitted?
    if request.method == 'POST':
        log.debug('Maintainer form submitted')
        form = RegistrationForm(None, request.POST)

        if form.is_valid():
            return _register_submit(request, form.cleaned_data)
    else:
        form = RegistrationForm(None)

    log.debug('Maintainer form requested')
    return render(request, 'register.html', {
        'settings': settings,
        'form': form
    })


@login_required
def profile(request):
    account_initial = {
        'name': request.user.name,
        'email': request.user.email
    }
    account_form = AccountForm(None, initial=account_initial)
    password_form = PasswordChangeForm(user=request.user)
    profile_form = ProfileForm(request.user, instance=request.user.profile)

    if request.method == 'POST':
        if 'commit_account' in request.POST:
            account_form = AccountForm(request.user, request.POST)

            if account_form.is_valid():
                log.debug('Updating user account for '
                          '{}'.format(request.user.email))
                _update_account(request, account_form.cleaned_data)

        if 'commit_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user,
                                               data=request.POST)

            if password_form.is_valid():
                log.debug('Changing password for account '
                          '{}'.format(request.user.email))
                password_form.save()
                update_session_auth_hash(request, password_form.user)

        if 'commit_profile' in request.POST:
            profile_form = ProfileForm(request.user, request.POST,
                                       instance=request.user.profile)

            if profile_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.user = request.user
                profile.save()

    return render(request, 'profile.html', {
        'settings': settings,
        'account_form': account_form,
        'password_form': password_form,
        'profile_form': profile_form
    })

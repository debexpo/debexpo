#   views.py — accounts views
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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

import logging
from datetime import datetime

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

from .forms import RegistrationForm, AccountForm, ProfileForm, GPGForm
from .models import Profile, User, UserStatus
from debexpo.keyring.models import Key

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
               activate_url=activate_url, settings=settings)


def _register_submit(request, info):
    """
    Handles the form submission for a maintainer account registration.
    """
    log.info('Creating new user {} <{}> as {}'.format(
        info.get('name'), info.get('email'),
        UserStatus(int(info.get('account_type'))).label
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


def _update_key(request, gpg_form):
    data = gpg_form.key
    key = gpg_form.save(commit=False)

    key.user = request.user
    key.size = data.size
    key.fingerprint = data.fingerprint
    key.algorithm = data.algorithm

    key.save()
    key.update_subkeys()


def _format_fingerprint(fingerprint):
    prettify = ''
    for index in range(0, len(fingerprint)):
        prettify += fingerprint[index]
        if not (index + 1) % 4:
            prettify += '&nbsp;'
        if not (index + 1) % 20:
            prettify += '&nbsp;'

    return prettify


def register(request):
    """
    Provides the form for a maintainer account registration.
    """
    # Has the form been submitted?
    if request.method == 'POST':
        log.debug('Maintainer form submitted')
        form = RegistrationForm(None, request.POST,
                                elapsed=request.session.get('timestamp', None),
                                ip=request.META['REMOTE_ADDR'])

        if form.is_valid():
            return _register_submit(request, form.cleaned_data)
    else:
        form = RegistrationForm(None)
        request.session['timestamp'] = str(datetime.now())

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
    gpg_fingerprint = None
    try:
        gpg_form = GPGForm(instance=request.user.key)
        gpg_fingerprint = _format_fingerprint(request.user.key.fingerprint)
    except Key.DoesNotExist:
        gpg_form = GPGForm()

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

        if 'commit_gpg' in request.POST:
            try:
                gpg_form = GPGForm(request.POST, instance=request.user.key)
            except Key.DoesNotExist:
                gpg_form = GPGForm(request.POST)

            if gpg_form.is_valid():
                _update_key(request, gpg_form)
                gpg_fingerprint = _format_fingerprint(
                    request.user.key.fingerprint
                )

        if 'delete_gpg' in request.POST:
            try:
                key = request.user.key
            except Key.DoesNotExist:
                pass
            else:
                key.delete()
                gpg_form = GPGForm()
                gpg_fingerprint = None

    return render(request, 'profile.html', {
        'settings': settings,
        'account_form': account_form,
        'password_form': password_form,
        'profile_form': profile_form,
        'gpg_form': gpg_form,
        'gpg_fingerprint': gpg_fingerprint,
    })

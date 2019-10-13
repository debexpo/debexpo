#   views.py — accounts views
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import RegistrationForm

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
    email = Email('password-creation.eml')
    activate_url = request.scheme + '://' + get_current_site(request).domain + \
        reverse('password_reset_confirm', kwargs={
            'uidb64': uid, 'token': token
        })
    email.send(_('Next step: Confirm your email address'), [recipient],
               activate_url=activate_url)


def _register_submit(request, info):
    """
    Handles the form submission for a maintainer account registration.
    """
    log.debug('Register form validated successfully')

    # Debexpo use the email field as the username
    user = User.objects.create_user(info.get('email'), info.get('email'))
    user.first_name = info.get('name')
    user.save()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    _send_activate_email(request, uid, token, user.email)

    log.debug('New user saved')
    return render(request, 'activate.html', {
        'settings': settings
    })


def register(request):
    """
    Provides the form for a maintainer account registration.
    """
    # Has the form been submitted?
    if request.method == 'POST':
        log.debug('Maintainer form submitted')
        form = RegistrationForm(request.POST)

        if form.is_valid():
            return _register_submit(request, form.cleaned_data)
    else:
        form = RegistrationForm()

    log.debug('Maintainer form requested')
    return render(request, 'register.html', {
        'settings': settings,
        'form': form
    })

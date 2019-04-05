# -*- coding: utf-8 -*-
#
#   register.py — Register Controller
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

"""
Holds the RegisterController.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import logging
from datetime import datetime

from debexpo.lib.base import BaseController, c, config, url, render, request, \
    abort, validate
from debexpo.lib import constants
from debexpo.lib.email import Email
from debexpo.lib.schemas import RegisterForm

from debexpo.model import meta
from debexpo.model.users import User

import debexpo.lib.utils

log = logging.getLogger(__name__)


class RegisterController(BaseController):

    def __init__(self):
        """
        Class constructor. Sets c.config for the templates.
        """
        c.config = config

    def _send_activate_email(self, key, recipient):
        """
        Sends an activation email to the potential new user.

        ``key``
            Activation key that's already stored in the database.

        ``recipient``
            Email address to send to.
        """
        log.debug('Sending activation email')
        email = Email('register_activate')
        activate_url = 'http://' + config['debexpo.sitename'] + \
            url.current(action='activate', id=key)
        email.send([recipient], activate_url=activate_url)

    @validate(schema=RegisterForm(), form='register')
    def _register_submit(self):
        """
        Handles the form submission for a maintainer account registration.
        """
        log.debug('Register form validated successfully')

        # Activation key.
        key = debexpo.lib.utils.random_hash()

        u = User(name=self.form_result['name'],
                 email=self.form_result['email'],
                 password=debexpo.lib.utils.hash_password(
                     self.form_result['password']),
                 lastlogin=datetime.now(),
                 verification=key)

        if self.form_result['sponsor'] == '1':
            u.status = constants.USER_STATUS_DEVELOPER

        meta.session.add(u)
        meta.session.commit()

        self._send_activate_email(key, self.form_result['email'])

        log.debug('New user saved')
        return render('/register/activate.mako')

    def register(self):
        """
        Provides the form for a maintainer account registration.
        """
        # Has the form been submitted?
        if request.method == 'POST':
            log.debug('Maintainer form submitted')
            return self._register_submit()
        else:
            log.debug('Maintainer form requested')
            return render('/register/register.mako')

    def activate(self, id):
        """
        Upon given a verification ID, activate an account.

        ``id``
            ID to use to verify the account.
        """
        log.debug('Activation request with key = %s' % id)

        user = meta.session.query(User).filter_by(verification=id).first()

        if user is not None:
            log.debug('Activating user "%s"' % user.name)
            user.verification = None
            meta.session.commit()
        else:
            log.error('Could not find user; redirecting to main page')
            abort(404, 'Could not find user; redirecting to main page')

        c.user = user
        return render('/register/activated.mako')

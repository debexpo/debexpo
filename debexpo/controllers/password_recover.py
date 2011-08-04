# -*- coding: utf-8 -*-
#
#   password_recover.py -- controller for doing web-based password recovery
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2011 Asheesh Laroia <paulproteus@debian.org>
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
Holds the PasswordResetController class.
"""

__author__ = 'Asheesh Laroia'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner, Copyright © 2011 Asheesh Laroia'
__license__ = 'MIT'

import logging
import os

from debexpo.lib.base import BaseController, validate, c,  _, request, render, url, abort
from debexpo.lib.schemas import PasswordResetForm
from debexpo.lib.email import Email
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.password_reset import PasswordReset
import debexpo.lib.utils
#from pylons import config

log = logging.getLogger(__name__)

class PasswordRecoverController(BaseController):
    """
    Helps people reset their passwords on the web.
    """

    @validate(schema=PasswordResetForm(), form='index')
    def _reset(self):
        """
        Manages submissions to the password reset form.
        """
        log.debug('Form validated successfully')
        try:
            u = meta.session.query(User).filter_by(email=self.form_result['email']).one()
        except:
            log.debug('Invalid email address somehow')
            c.message = _('We do not have an account with that email address')
            return self.index(get=True)

        # If that worked, then we send the user an email with a temporary URL
        # they can use to have our system generate a new password for them.
        log.debug('Sending activation email')

        email = Email('password_reset')
        password_reset_data = PasswordReset.create_for_user(u)
        meta.session.add(password_reset_data)
        meta.session.commit()

        recipient = u.email
        password_reset_url = 'http://' + request.host + url.current(
            action='actually_reset_password', id=password_reset_data.temporary_auth_key)
        email.send([recipient], password_reset_url=password_reset_url)

        # FIXME: This should be a HTTP redirect
        return render('/password_recover/_reset.mako')

    def actually_reset_password(self, id):
        '''The point of this controller is to take a temporary auth key as input.

        If it is a valid one, change the password for that user to a randomly-
        generated string.

        If it is not a valid one, generate a 404.'''
        try:
            pr = meta.session.query(PasswordReset).filter_by(
                temporary_auth_key=id).one()
        except:
            log.debug('Invalid temporary auth key')
            abort(404,
                  "We do not know about that particular password reset key.")

        # Okay, so we got a user. Good.
        u = pr.user

        # Give the user a random password
        raw_password = debexpo.lib.utils.random_hash()[:10]

        # FIXME: We should not set u.password directly. Instead, we should
        # use a helper from the User model or something.
        u.password = debexpo.lib.utils.hash_it(raw_password)
        meta.session.commit()

        log.debug('Password reset successful; saving user object')
        c.new_password = raw_password
        return render('/password_recover/actually_reset_password.mako')

    def index(self, get=False):
        """
        Entry point. Displays the password reset form.

        ``get``
            If True, display the form even if request.method is POST.
        """

        if not hasattr(c, 'message'):
            c.message = None

        if request.method == 'POST' and get is False:
            log.debug(
                'Password recovery form submitted with email = "%s"' %
                request.POST.get('email'))
            return self._reset()
        else:
            return render('/password_recover/index.mako')

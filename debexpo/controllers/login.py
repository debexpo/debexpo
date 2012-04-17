# -*- coding: utf-8 -*-
#
#   login.py — Login controller
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
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
Holds the LoginController class.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import logging
from datetime import datetime

from debexpo.lib.base import BaseController, validate, config, c, session, _, redirect, request, render, url
from debexpo.lib.schemas import LoginForm
from debexpo.model import meta
from debexpo.model.users import User

import debexpo.lib.utils

log = logging.getLogger(__name__)

class LoginController(BaseController):
    """
    Manages login requests.
    """

    def __init__(self):
        """
        Class constructor. Sets common template variables.
        """
        c.config = config
        c.message = None

    @validate(schema=LoginForm(), form='index')
    def _login(self):
        """
        Manages submissions to the login form.
        """
        log.debug('Form validated successfully')
        password = debexpo.lib.utils.hash_it(self.form_result['password'])

        u = None
        try:
            u = meta.session.query(User).filter_by(email=self.form_result['email']).filter_by(password=password).filter_by(verification=None).one()
        except:
            log.debug('Invalid email or password')
            c.message = _('Invalid email or password')
            return self.index(True)

        session['user_id'] = u.id
        session['user_type'] = u.type
        session.save()

        log.debug('Authentication successful; saving session')

        u.lastlogin = datetime.now()

        # Clear the 'path_before_login' once it was used once. This is necessary to make sure users won't be redirected
        # to pages which don't exist anymore, as the path may have been stored in the session for a long time. Consider
        # following use case:
        # a) User is not logged in
        # b) User opens the URL /package/sunflow/delete/... in the browser
        # c) User is being redirected to /login, he logs in and is being redirected
        #    to the URL in b). This deletes the package, but leaves the URL in the session.
        # d) Once the user is trying to log in again - possibly after several weeks, the URL from
        #    b) is still in the session - but it may not exist anymore.
        if 'path_before_login' in session:
                path = session['path_before_login']
                del(session['path_before_login'])
        else:
                path = url('my')

        meta.session.commit()
        redirect(path)

    def index(self, get=False):
        """
        Entry point. Displays the login form.

        ``get``
            If True, display the form even if request.method is POST.
        """


        c.request = request
        if request.method == 'POST' and get is False:
            log.debug('Login form submitted with email = "%s"' % request.POST.get('email'))
            return self._login()
        else:
            return render('/login/index.mako')

    def logout(self):
        """Logs the current user out."""
        if 'user_id' in session:
            log.debug('User #%s logged out.' % session['user_id'])
            del session['user_id']
        if 'user_type' in session:
            del session['user_type']
        session.save()
        redirect(url('index'))

# -*- coding: utf-8 -*-
#
#   register.py — Register Controller
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonnylamb@jonnylamb.com
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
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging
import md5
import random
from datetime import datetime

from debexpo.lib.base import *
from debexpo.lib import constants
from debexpo.lib.email import Email
from debexpo.lib.schemas import MaintainerForm, SponsorForm

from debexpo.model import meta
from debexpo.model.users import User

log = logging.getLogger(__name__)

class RegisterController(BaseController):

    def __init__(self):
        """
        Class constructor. Sets c.config for the templates.
        """
        c.config = config

    def index(self):
        """
        Entry point to controller. Displays the index page.
        """
        log.debug('Main register form requested')

        if config['debexpo.debian_specific'] != 'true':
            log.error('debexpo.debian_specific is !true; redirecting to maintainer form')
            h.redirect_to(h.url_for(action='maintainer'))

        return render('/register/index.mako')

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
        url = 'http://' + request.host + h.url_for(action='activate', id=key)
        email.send([recipient], activate_url=url)

    @validate(schema=MaintainerForm(), form='maintainer')
    def _maintainer_submit(self):
        """
        Handles the form submission for a maintainer account registration.
        """
        log.debug('Maintainer form validated successfully')

        # Activation key.
        key = md5.new(str(random.random())).hexdigest()

        u = User(name=self.form_result['name'],
            email=self.form_result['email'],
            password=md5.new(self.form_result['password']).hexdigest(),
            lastlogin=datetime.now(),
            verification=key)

        meta.session.save(u)
        meta.session.commit()

        self._send_activate_email(key, self.form_result['email'])

        log.debug('New user saved')
        return render('/register/activate.mako')

    def maintainer(self):
        """
        Provides the form for a maintainer account registration.
        """
        # Has the form been submitted?
        if request.method == 'POST':
            log.debug('Maintainer form submitted')
            return self._maintainer_submit()
        else:
            log.debug('Maintainer form requested')
            return render('/register/maintainer.mako')

    @validate(schema=SponsorForm(), form='sponsor')
    def _sponsor_submit(self):
        """
        Handles the form submission for a sponsor account registration.
        """
        log.debug('Sponsor form validated successfully')

        # Activation key.
        key = md5.new(str(random.random())).hexdigest()

        u = User(name=self.form_result['name'],
            email=self.form_result['email'],
            password=md5.new(self.form_result['password']).hexdigest(),
            lastlogin=datetime.now(),
            verification=key,
            status=constants.USER_STATUS_DEVELOPER)

        meta.session.save(u)
        meta.session.commit()

        self._send_activate_email(key, self.form_result['email'])

        log.debug('New user saved')
        return render('/register/activate.mako')

    def sponsor(self):
        """
        Provides the form for a sponsor account registration.
        """
        if config['debexpo.debian_specific'] != 'true':
            log.error('Sponsor form requested when debexpo.debian_specific option set to !true; redirecting to maintainer form')
            h.redirect_to(h.url_for(action='maintainer'))

        # Has the form been submitted?
        if request.method == 'POST':
            log.debug('Sponsor form submitted')
            return self._sponsor_submit()
        else:
            log.debug('Sponsor form requested')
            return render('/register/sponsor.mako')

    def activate(self, id):
        """
        Upon given a verification ID, activate an account.

        ``id``
            ID to use to verify the account.
        """
        log.debug('Activation request with key = %s' % id)

        if id is None:
            log.error('Key is None; redirecting to main page')
            h.redirect_to(h.url_for(action=None))

        user = meta.session.query(User).filter_by(verification=id).first()

        if user is not None:
            log.debug('Activating user "%s"' % user.name)
            user.verification = None
            meta.session.commit()
        else:
            log.error('Could not find user; redirecting to main page')
            h.redirect_to(h.url_for(action=None, id=None))

        c.user = user
        return render('/register/activated.mako')

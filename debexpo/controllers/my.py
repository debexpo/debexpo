# -*- coding: utf-8 -*-
#
#   my.py — My Controller
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
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
Holds the MyController.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging
import md5

from debexpo.lib.base import *
from debexpo.lib import constants, form
from debexpo.lib.schemas import DetailsForm, GpgForm, PasswordForm, OtherDetailsForm
from debexpo.lib.gnupg import GnuPG

from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.user_countries import UserCountry

log = logging.getLogger(__name__)

class MyController(BaseController):
    """
    Controller for handling /my.
    """
    requires_auth = True

    def __init__(self):
        """
        Class constructor. Sets common class and template attributes.
        """
        c.config = config
        self.user = None
        self.gnupg = GnuPG()

    def _details(self):
        """
        Handles a user submitting the details form.
        """
        log.debug('Validating details form')
        try:
            fields = form.validate(DetailsForm, user_id=self.user.id)
        except Exception, e:
            log.error('Failed validation')
            return form.htmlfill(self.index(get=True), e)

        log.debug('Validation successful')
        self.user.name = fields['name']
        self.user.email = fields['email']

        meta.session.commit()

        log.debug('Saved name and email and redirecting')
        return redirect_to(h.url_for('my', action=None))

    @validate(schema=GpgForm(), form='index')
    def _gpg(self):
        """
        Handles a user submitting the GPG form.
        """
        log.debug('GPG form validated successfully')

        # Should the key be deleted?
        if self.form_result['delete_gpg'] and self.user.gpg is not None:
            log.debug('Deleting current GPG key')
            self.user.gpg = None
            self.user.gpg_id = None

        # Should the key be updated.
        if 'gpg' in self.form_result and self.form_result['gpg'] is not None:
            log.debug('Setting a new GPG key')
            self.user.gpg = self.form_result['gpg'].value
            self.user.gpg_id = self.gnupg.parse_key_id(self.user.gpg)

        meta.session.commit()

        log.debug('Saved key changes and redirecting')
        return redirect_to(h.url_for('my', action=None))

    @validate(schema=PasswordForm(), form='index')
    def _password(self):
        """
        Handles a user submitting the password form.
        """
        log.debug('Password form validated successfully')

        # Simply set password.
        self.user.password = md5.new(self.form_result['password_new']).hexdigest()
        meta.session.commit()
        log.debug('Saved new password and redirecting')

        return redirect_to(h.url_for('my', action=None))

    @validate(schema=OtherDetailsForm(), form='index')
    def _other_details(self):
        """
        Handles a user submitting the other details form.
        """
        log.debug('Other details form validated successfully')

        # A country ID of -1 means the country shouldn't be set.
        if self.form_result['country'] == -1:
            self.user.country = None
        else:
            self.user.country_id = self.form_result['country']

        self.user.ircnick = self.form_result['ircnick']
        self.user.jabber = self.form_result['jabber']

        # Only set these values if the checkbox was shown in the form.
        if config['debexpo.debian_specific'] == 'true':
            if self.user.status != constants.USER_STATUS_DEVELOPER:
                if self.form_result['status']:
                    self.user.status = constants.USER_STATUS_MAINTAINER
                else:
                    self.user.status = constants.USER_STATUS_NORMAL

        meta.session.commit()
        log.debug('Saved other details and redirecting')

        return redirect_to(h.url_for('my', action=None))

    def index(self, get=False):
        """
        Controller entry point. Displays forms to change user details.

        ``get``
            Whether to ignore request.method and assume it's a GET. This is useful
            for validators to re-display the form if there's something wrong.
        """
        # Get User object.
        log.debug('Getting user object for user_id = "%s"' % session['user_id'])
        self.user = meta.session.query(User).get(session['user_id'])

        if self.user is None:
            # Cannot find user from user_id.
            log.debug('Cannot find user from user_id')
            return redirect_to(h.url_for(controller='login'))

        log.debug('User object successfully selected')

        # A form has been submit.
        if request.method == 'POST' and get is False:
            log.debug('A form has been submit')
            try:
                return { 'details' : self._details,
                  'gpg' : self._gpg,
                  'password' : self._password,
                  'other_details' : self._other_details
                }[request.params['form']]()
            except KeyError:
                log.error('Could not find form name; defaulting to main page')
                pass

        log.debug('Populating template context')

        # The template will need to look at the user details.
        c.user = self.user

        # Create the countries values.
        countries = { '' : -1 }

        for country in meta.session.query(UserCountry).all():
            countries[country.name] = country.id

        c.countries = countries

        if self.user.country is None:
            c.current_country = -1
        else:
            c.current_country = self.user.country.id

        # Toggle whether Debian developer/maintainer forms should be shown.
        if self.user.status == constants.USER_STATUS_DEVELOPER:
            c.debian_developer = True
        else:
            if self.user.status == constants.USER_STATUS_MAINTAINER:
                c.debian_maintainer = True
            else:
                c.debian_maintainer = False

        # Enable the form to show information on the user's GPG key.
        if self.user.gpg is not None:
            c.currentgpg = c.user.gpg_id

        log.debug('Rendering page')
        return render('/my/index.mako')

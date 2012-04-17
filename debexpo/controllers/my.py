# -*- coding: utf-8 -*-
#
#   my.py — My Controller
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
Holds the MyController.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import logging
import tempfile

from debexpo.lib.base import *
from debexpo.lib import constants, form
from debexpo.lib.schemas import DetailsForm, GpgForm, PasswordForm, OtherDetailsForm, MetricsForm
from debexpo.lib.gnupg import GnuPG

from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.user_countries import UserCountry
from debexpo.model.sponsor_metrics import SponsorMetrics, SponsorMetricsTags, SponsorTags
from debexpo.model.data_store import DataStore

from sqlalchemy.orm import joinedload

import debexpo.lib.utils

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
        redirect(url('my'))

    @validate(schema=GpgForm(), form='index')
    def _gpg(self):
        """
        Handles a user submitting the GPG form.
        """
        log.debug('GPG form validated successfully')
        self.gpg = GnuPG()

        # Should the key be deleted?
        if self.form_result['delete_gpg'] and self.user.gpg is not None:
            keyid = self.gnupg.extract_key_id(self.user.gpg_id)
            log.debug('Deleting current GPG key %s' % (keyid))
            (out, err) = self.gnupg.remove_signature(keyid)
            if err != 0:
                log.error("gpg failed to delete keyring: %s" % (out))
                abort(500)
            self.user.gpg = None
            self.user.gpg_id = None

        # Should the key be updated.
        if 'gpg' in self.form_result and self.form_result['gpg'] is not None:
            log.debug('Setting a new GPG key')
            self.user.gpg = self.form_result['gpg'].value
            (self.user.gpg_id, _) = self.gnupg.parse_key_id(self.user.gpg)

            temp = tempfile.NamedTemporaryFile(delete=True)
            temp.write(self.user.gpg)
            temp.flush()
            (out, err) = self.gpg.add_signature(temp.name)
            temp.close()
            if err != 0:
                log.error("gpg failed to import keyring: %s" % (out))
                abort(500)
            log.debug(out)



        meta.session.commit()

        log.debug('Saved key changes and redirecting')
        redirect(url('my'))

    @validate(schema=PasswordForm(), form='index')
    def _password(self):
        """
        Handles a user submitting the password form.
        """
        log.debug('Password form validated successfully')

        # Simply set password.
        self.user.password = debexpo.lib.utils.hash_it(self.form_result['password_new'])
        meta.session.commit()
        log.debug('Saved new password and redirecting')

        redirect(url('my'))

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

        redirect(url('my'))

    @validate(schema=MetricsForm(), form='index')
    def _metrics(self):
        """
        Handles a user submitting the metrics form.
        """
        log.debug('Metrics form validated successfully')

        if 'user_id' not in session:
            log.debug('Requires authentication')
            session['path_before_login'] = request.path_info
            session.save()
            redirect(url('login'))

        sm = SponsorMetrics(user_id=session['user_id'])
        sm.contact = int(self.form_result['preferred_contact_method'])
        #XXX TODO: WTF?! Find out why on earth package_types is no string
        sm.types = str(self.form_result['package_types'])
        sm.guidelines_text = self.form_result['packaging_guideline_text']
        sm.social_requirements = self.form_result['social_requirements']
        sm.availability = self.form_result['availability']

        if self.form_result['packaging_guidelines'] == constants.SPONSOR_GUIDELINES_TYPE_URL:
            sm.guidelines = constants.SPONSOR_GUIDELINES_TYPE_URL
        elif self.form_result['packaging_guidelines'] == constants.SPONSOR_GUIDELINES_TYPE_TEXT:
            sm.guidelines = constants.SPONSOR_GUIDELINES_TYPE_TEXT
        else:
            sm.guidelines = constants.SPONSOR_GUIDELINES_TYPE_NONE

        for tag in meta.session.query(SponsorTags).all():
            if tag.tag in self.form_result:
                log.debug("Weighten tag %s to %s" % (tag.tag, self.form_result[tag.tag]))
                metrics = SponsorMetricsTags(tag=tag.tag, user_id=session['user_id'], weight=self.form_result[tag.tag])
                sm.tags.append(metrics)

        meta.session.merge(sm)
        meta.session.commit()

        redirect(url('my'))

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
            redirect(url('login'))

        log.debug('User object successfully selected')

        # A form has been submit.
        if request.method == 'POST' and get is False:
            log.debug('A form has been submit')
            try:
                return { 'details' : self._details,
                  'gpg' : self._gpg,
                  'password' : self._password,
                  'other_details' : self._other_details,
                  'metrics' : self._metrics,
                }[request.params['form']]()
            except KeyError:
                log.error('Could not find form name "%s"; defaulting to main page' % (request.params['form']))
                pass

        log.debug('Populating template context')

        # The template will need to look at the user details.
        c.user = self.user

        # Create the countries values.
        countries = { -1: '' }

        for country in meta.session.query(UserCountry).all():
            countries[country.id] = country.name

        c.countries = countries

        if self.user.country is None:
            c.current_country = -1
        else:
            c.current_country = self.user.country.id

        # Toggle whether Debian developer/maintainer forms should be shown.
        if self.user.status == constants.USER_STATUS_DEVELOPER:
            c.debian_developer = True
            c.debian_maintainer = False
        else:
            c.debian_developer = False
            if self.user.status == constants.USER_STATUS_MAINTAINER:
                c.debian_maintainer = True
            else:
                c.debian_maintainer = False

        # Enable the form to show information on the user's GPG key.
        if self.user.gpg is not None:
            c.currentgpg = c.user.gpg_id
        else:
            c.currentgpg = None

        if self.user.status == constants.USER_STATUS_DEVELOPER:
            # Fill in various sponsor metrics
            c.constants = constants
            c.contact_methods = [
                (constants.SPONSOR_CONTACT_METHOD_NONE, _('None')),
                (constants.SPONSOR_CONTACT_METHOD_EMAIL, _('Email')),
                (constants.SPONSOR_CONTACT_METHOD_IRC, _('IRC')),
                (constants.SPONSOR_CONTACT_METHOD_JABBER, _('Jabber')),
                ]

            c.metrics = meta.session.query(SponsorMetrics)\
                .options(joinedload(SponsorMetrics.user))\
                .options(joinedload(SponsorMetrics.tags))\
                .filter_by(user_id = session['user_id'])\
                .first()
            c.technical_tags = meta.session.query(SponsorTags).filter_by(tag_type=constants.SPONSOR_METRICS_TYPE_TECHNICAL).all()
            c.social_tags = meta.session.query(SponsorTags).filter_by(tag_type=constants.SPONSOR_METRICS_TYPE_SOCIAL).all()
            if not c.metrics:
                # Set some sane defaults
                log.debug("Generating new defaults for sponsor metrics")
                c.metrics = SponsorMetrics()
                c.metrics.availability = constants.SPONSOR_METRICS_PRIVATE
                c.metrics.guidelines = constants.SPONSOR_GUIDELINES_TYPE_NONE


        log.debug('Rendering page')
        return render('/my/index.mako')

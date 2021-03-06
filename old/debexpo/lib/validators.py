# -*- coding: utf-8 -*-
#
#   validators.py — formencode validators for debexpo
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
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
Holds the formencode validators for debexpo.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import formencode
import logging
from pylons.i18n import _

from debexpo.lib.base import session, config
from debexpo.lib.gnupg import GnuPG, ExceptionGnuPGMultipleKeys

from debexpo.model import meta
from debexpo.model.users import User
from debexpo.lib import constants

import debexpo.lib.utils

log = logging.getLogger(__name__)


class GpgKey(formencode.validators.FieldStorageUploadConverter):
    """
    Validator for an uploaded GPG key. They must with the 'BEGIN PGP PUBLIC KEY
    BLOCK' text.
    """

    def __init__(self):
        self.gpg_id = None
        self.gnupg = GnuPG()

    def _to_python(self, value, c):
        """
        Validate the GPG key.

        ``value``
            FieldStorage uploaded file.

        ``c``
        """
        if not value.value.startswith('-----BEGIN PGP PUBLIC KEY BLOCK-----'):
            log.error('GPG key does not start with BEGIN PGP PUBLIC KEY BLOCK')
            raise formencode.Invalid(_('Invalid GPG key'), value, c)

        if self.gnupg.is_unusable():
            log.error('Unable to validate GPG key because gpg is unusable.')
            raise formencode.Invalid(_('Internal error: debexpo is not ' +
                                       'properly configured to handle' +
                                       'GPG keys'), value, c)

        try:
            (self.gpg_id, user_ids) = self.gnupg.parse_key_id(value.value)
        except ExceptionGnuPGMultipleKeys:
            raise formencode.Invalid(_('Multiple keys not supported'), value, c)

        if self.gpg_id is None:
            log.error("Failed to parse GPG key")
            raise formencode.Invalid(_('Invalid GPG key'), value, c)

        """
        allow only keys which match the user name
        """

        user = meta.session.query(User).get(session['user_id'])
        for (uid, email) in user_ids:
            if user.email == email:
                break
        else:
            log.debug("User id {} [{}]: fail to upload GPG key: no uid "
                      "matching email <{}>".format(user.id,
                                                   user.name.encode('utf-8'),
                                                   user.email))
            raise formencode.Invalid(_('None of your user IDs in key %s does '
                                       'match your profile mail address' %
                                       (self.gpg_id)), value, c)

        """
        Minimum Key Strength Check.
        """

        requiredkeystrength = int(config['debexpo.gpg_minkeystrength'])
        keystrength = self.gnupg.extract_key_strength(self.key_id())
        keytype = self.gnupg.extract_key_type(self.key_id())

        if keytype == 'R':
            if keystrength < requiredkeystrength:
                log.debug("Key strength unacceptable in Debian Keyring")
                raise formencode.Invalid(_('Key strength unacceptable in '
                                           'Debian Keyring. The minimum '
                                           'required key strength is %s bits.' %
                                           str(requiredkeystrength)), value, c)
        elif keytype == 'E' and keystrength == 256:
            # ECDSA keys have a fixed size.
            pass
        else:
            log.debug("Key type unacceptable in Debian Keyring")
            raise formencode.Invalid(_('Key type unacceptable in Debian '
                                       'Keyring. It must be RSA or ECDSA.'),
                                     value, c)

        return formencode.validators.FieldStorageUploadConverter \
            ._to_python(self, value, c)

    def key_id(self):
        return self.gpg_id


class CurrentPassword(formencode.validators.String):
    """
    Validator for a current password depending on the session's user_id.
    """

    def _to_python(self, value, c):
        """
        Validate the password.
        """
        user = meta.session.query(User).get(session['user_id'])

        if not debexpo.lib.utils.validate_password(user, value):
            raise formencode.Invalid(_('Incorrect password'), value, c)

        return formencode.validators.String._to_python(self, value, c)


class CheckBox(formencode.validators.Int):
    """
    Validator for a checkbox. When not checked, it doesn't send, and formencode
    complains.
    """
    if_missing = None


class NewEmailToSystem(formencode.validators.Email):
    """
    Email validator class to make sure there is not another user with
    the same email address already registered.
    """
    def _to_python(self, value, c=None):
        """
        Validate the email address.

        ``value``
            Address to validate.

        ``c``
        """
        u = meta.session.query(User).filter_by(email=value)

        # c.user_id can contain a user_id that should be ignored (i.e. when the
        # user wants to keep the same email).
        if hasattr(c, 'user_id'):
            u = u.filter(User.id != c.user_id)

        u = u.first()

        if u is not None:
            log.error('Email %s already found on system' % value)
            raise formencode.Invalid(_('A user with this email address is '
                                       'already registered on the system'),
                                     value, c)

        return formencode.validators.Email._to_python(self, value, c)


class NewNameToSystem(formencode.FancyValidator):
    """
    Name validation class to make sure there is not another user with
    the same name already registered.
    """
    def _to_python(self, value, c=None):
        """
        Validate the name address.

        ``value``
            Name to validate.

        ``c``
        """
        u = meta.session.query(User).filter_by(name=value)

        # c.user_id can contain a user_id that should be ignored (i.e. when the
        # user wants to keep the same email).
        if hasattr(c, 'user_id'):
            u = u.filter(User.id != c.user_id)

        u = u.first()

        if u is not None:
            log.error('Name %s already found on system' % value)
            raise formencode.Invalid(_('A user with this name is already '
                                       'registered on the system. If it is '
                                       'you, use that account! Otherwise use a '
                                       'different name to register.'), value, c)

        return value


def ValidateSponsorEmail(values, state, validator):
    if values['sponsor'] == '1' and not values['email'].endswith('@debian.org'):
        return {'sponsor': 'A sponsor account must be registered with '
                           'your @debian.org address'}


class DummyValidator(formencode.FancyValidator):
    pass


def ValidatePackagingGuidelines(values, state, validator):
    try:
        if (values['packaging_guidelines'] ==
                constants.SPONSOR_GUIDELINES_TYPE_TEXT):
            formencode.validators.String(min=1) \
                .to_python(values['packaging_guideline_text'])
        elif (values['packaging_guidelines'] ==
                constants.SPONSOR_GUIDELINES_TYPE_URL):
            formencode.validators.URL(add_http=True) \
                .to_python(values['packaging_guideline_text'])
        else:
            formencode.validators.Empty() \
                .to_python(values['packaging_guideline_text'])
    except Exception as e:
        return {'packaging_guideline_text': e}
    return None

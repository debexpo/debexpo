# -*- coding: utf-8 -*-
#
#   schemas.py — Form schemas
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
Holds form schemas for debexpo forms.
"""

__author__ = 'Jonny Lamb, Jan Dittberner'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import formencode

from pylons import config

from debexpo.lib import constants
from debexpo.lib.validators import NewEmailToSystem, GpgKey, \
    CurrentPassword, CheckBox, NewNameToSystem, ValidateSponsorEmail

class LoginForm(formencode.Schema):
    """
    Schema for the login form in the login controller.
    """
    email = formencode.validators.Email(not_empty=True)
    password = formencode.validators.String(not_empty=True)
    commit = formencode.validators.String()


class MyForm(formencode.Schema):
    """
    General schema for all forms in the my controller to extend.
    """
    commit = formencode.validators.String()
    form = formencode.validators.String()

class DetailsForm(MyForm):
    """
    Schema for updating user details in the my controller.
    """
    name = formencode.validators.String(not_empty=True)
    email = NewEmailToSystem(not_empty=True)

class GpgForm(MyForm):
    """
    Schema for updating the user's GPG key in the my controller.
    """
    gpg = GpgKey()
    delete_gpg = formencode.validators.Int()

class PasswordForm(MyForm):
    """
    Schema for updating the user's password in the my controller.
    """
    password_current = CurrentPassword()
    password_confirm = formencode.validators.String(min=6)
    password_new = formencode.validators.String(min=6)

    # Make sure password_new and password_confirm are the same.
    chained_validators = [
        formencode.validators.FieldsMatch('password_new', 'password_confirm')
    ]

class OtherDetailsForm(MyForm):
    """
    Schema for updating other details: country, jabber, ircnick and status
    in the my controller.
    """
    country = formencode.validators.Number()
    ircnick = formencode.validators.String()
    jabber = formencode.validators.String()
    status = CheckBox()

class RegisterForm(formencode.Schema):
    """
    Schema for the general fields in the register controller. The maintainer
    and sponsor forms should extend this.
    """
    name = NewNameToSystem(not_empty=True)
    password = formencode.validators.String(min=6)
    password_confirm = formencode.validators.String(min=6)
    commit = formencode.validators.String()
    sponsor = formencode.validators.String(min=1, max=1)
    email = NewEmailToSystem(not_empty=True)

    # Make sure password and password_confirm are the same.
    chained_validators = [
        formencode.validators.FieldsMatch('password', 'password_confirm'),
        formencode.schema.SimpleFormValidator(ValidateSponsorEmail),
    ]


class PackageSubscribeForm(formencode.Schema):
    """
    Schema for the package email subscription form.
    """
    level = formencode.compound.All(
        formencode.validators.OneOf([
                -1, constants.SUBSCRIPTION_LEVEL_UPLOADS,
                 constants.SUBSCRIPTION_LEVEL_COMMENTS]),
        formencode.validators.Int(not_empty=True))
    commit = formencode.validators.String()

class PackageCommentForm(formencode.Schema):
    """
    Schema for the package comment form.
    """
    package_version = formencode.validators.Int(not_empty=True)
    text = formencode.validators.String(not_empty=True)
    outcome = formencode.compound.All(
        formencode.validators.OneOf([
                constants.PACKAGE_COMMENT_OUTCOME_UNREVIEWED,
                constants.PACKAGE_COMMENT_OUTCOME_NEEDS_WORK,
                constants.PACKAGE_COMMENT_OUTCOME_PERFECT]),
        formencode.validators.Int(not_empty=True))
    status = formencode.validators.Bool(if_missing=False)
    commit = formencode.validators.String()

class PasswordResetForm(formencode.Schema):
    """
    Schema for the password reset form in the password reset controller.
    """
    email = formencode.validators.Email(not_empty=True)
    commit = formencode.validators.String()




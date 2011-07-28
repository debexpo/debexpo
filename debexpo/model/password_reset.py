# -*- coding: utf-8 -*-
#
#   password_reset.py — model for temporary passwords related to password resets
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
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
Holds Password Reset model.
"""

__author__ = 'Asheesh Laroia'
__copyright__ = 'Copyright © 2011 Asheesh Laroia'
__license__ = 'MIT'

import hashlib
import os
import datetime

import sqlalchemy as sa
from sqlalchemy import orm

from debexpo.model import meta, OrmObject
from debexpo.model.users import User

PASSWORD_RESET_VALID_DAYS=7

t_password_reset = sa.Table(
    'password_reset', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('user_id', sa.types.Integer, sa.ForeignKey('users.id')),
    sa.Column('temporary_auth_key', sa.types.String(200), nullable=False, unique=False),
    sa.Column('valid_until', sa.types.DateTime, nullable=False),
    )

class PasswordReset(OrmObject):
    foreign = ['user']

    @staticmethod
    def create_for_user(u):
        obj = PasswordReset()
        obj.user = u
        obj.temporary_auth_key = hashlib.md5(os.urandom(20)).hexdigest()[:10]
        obj.valid_until = datetime.datetime.utcnow() + datetime.timedelta(
            days=PASSWORD_RESET_VALID_DAYS)
        return obj

orm.mapper(PasswordReset, t_password_reset, properties={
    'user' : orm.relation(User)
})

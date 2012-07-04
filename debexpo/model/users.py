# -*- coding: utf-8 -*-
#
#   users.py — users table model
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
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
Holds users table model.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import sqlalchemy as sa
from sqlalchemy import orm

import os

from debexpo.model import meta, OrmObject
from debexpo.model.user_countries import UserCountry
from debexpo.lib.constants import USER_TYPE_NORMAL, USER_STATUS_NORMAL
import debexpo.lib.utils

t_users = sa.Table('users', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('name', sa.types.String(200), nullable=False),
    sa.Column('email', sa.types.String(200), nullable=False),
    sa.Column('gpg', sa.types.Text, nullable=True),
    sa.Column('gpg_id', sa.types.String(30), nullable=True),
    sa.Column('password', sa.types.String(200), nullable=False),
    sa.Column('lastlogin', sa.types.DateTime, nullable=False),
    sa.Column('type', sa.types.Integer, nullable=False, default=USER_TYPE_NORMAL),
    sa.Column('status', sa.types.Integer, nullable=False, default=USER_STATUS_NORMAL),
    sa.Column('country_id', sa.types.Integer, sa.ForeignKey('user_countries.id')),
    sa.Column('ircnick', sa.types.String(200), nullable=True),
    sa.Column('jabber', sa.types.String(200), nullable=True),
    sa.Column('verification', sa.types.String(200), nullable=True),
    sa.Column('dmup', sa.types.Boolean, default=False),
    )

class User(OrmObject):
    foreign = ['country']

    def get_upload_key(self):
        import debexpo.model.user_upload_key
        keys = meta.session.query(debexpo.model.user_upload_key.UserUploadKey
            ).filter_by(user=self)
        if keys.count() > 0:
            return keys[0].upload_key
        else:
            # create one
            instance = debexpo.model.user_upload_key.UserUploadKey()
            instance.user_id = self.id
            instance.upload_key = debexpo.lib.utils.random_hash()
            meta.session.add(instance)
            meta.session.commit()
            return self.get_upload_key()

orm.mapper(User, t_users, properties={
    'country' : orm.relation(UserCountry, backref='users')
})

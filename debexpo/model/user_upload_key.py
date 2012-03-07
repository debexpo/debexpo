# -*- coding: utf-8 -*-
#
#   user_upload_key.py — model for upload keys
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
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
Holds users table model.
"""

__author__ = 'Asheesh Laroia'
__copyright__ = 'Copyright © 2011 Asheesh Laroia'
__license__ = 'MIT'

import sqlalchemy as sa
from sqlalchemy import orm

from debexpo.model import meta, OrmObject
from debexpo.model.users import User

t_user_upload_key = sa.Table('user_upload_key', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('user_id', sa.types.Integer, sa.ForeignKey('users.id')),
    sa.Column('upload_key', sa.types.String(200), nullable=False, unique=False),
    )

class UserUploadKey(OrmObject):
    foreign = ['user']

orm.mapper(UserUploadKey, t_user_upload_key, properties={
    'user' : orm.relation(User)
})

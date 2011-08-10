# -*- coding: utf-8 -*-
#
#   packages.py — packages table model
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
Holds packages table model.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import sqlalchemy as sa
from sqlalchemy import orm

from debexpo.model import meta, OrmObject
from debexpo.model.users import User
from debexpo.lib.constants import PACKAGE_NEEDS_SPONSOR_UNKNOWN

t_packages = sa.Table('packages', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('name', sa.types.String(200), nullable=False),
    sa.Column('user_id', sa.types.Integer, sa.ForeignKey('users.id')),
    sa.Column('description', sa.types.String(8192), nullable=True),
    sa.Column('watch_counter', sa.types.Integer, default=0),
    sa.Column('download_counter', sa.types.Integer, default=0),
    sa.Column('needs_sponsor', sa.types.Integer, nullable=False, default=PACKAGE_NEEDS_SPONSOR_UNKNOWN),
    )

class Package(OrmObject):
    foreign = ['user']

    def get_description_nl2br(self):
        s = self.description
        s = s.replace('<', '&lt;'
        s = s.replace('\n', '<br />')
        return s

orm.mapper(Package, t_packages, properties={
    'user' : orm.relation(User, backref='packages')
})

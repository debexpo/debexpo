# -*- coding: utf-8 -*-
#
#   package_info.py — package_info table model
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
Holds package_info table model.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import json

import sqlalchemy as sa
from sqlalchemy import orm

from debexpo.model import meta, OrmObject
from debexpo.model.package_versions import PackageVersion

t_package_info = sa.Table('package_info', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('package_version_id', sa.types.Integer, sa.ForeignKey('package_versions.id')),
    sa.Column('from_plugin', sa.types.String(200), nullable=False),
    sa.Column('outcome', sa.types.String(200), nullable=False),
    sa.Column('data', sa.types.Text, nullable=True),
    sa.Column('severity', sa.types.Integer, nullable=False),
    )

class PackageInfo(OrmObject):
    foreign = ['package_version']

    @property
    def rich_data(self):
        try:
            return json.loads(self.data)
        except ValueError:
            return self.data

    @rich_data.setter
    def rich_data(self, value):
        self.data = json.dumps(value)

orm.mapper(PackageInfo, t_package_info, properties={
    'package_version' : orm.relation(PackageVersion, backref='package_info'),
})

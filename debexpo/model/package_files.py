# -*- coding: utf-8 -*-
#
#   package_files.py — package_files table model
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
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
Holds package_files table model.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import backref

from debexpo.model import meta, OrmObject
from debexpo.model.binary_packages import BinaryPackage
from debexpo.model.source_packages import SourcePackage

t_package_files = sa.Table('package_files', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('binary_package_id', sa.types.Integer, sa.ForeignKey('binary_packages.id'), nullable=True),
    sa.Column('source_package_id', sa.types.Integer, sa.ForeignKey('source_packages.id'), nullable=True),
    sa.Column('filename', sa.types.String(200), nullable=False),
    sa.Column('size', sa.types.Integer, nullable=False),
    sa.Column('md5sum', sa.types.String(200), nullable=False),
    )

class PackageFile(OrmObject):
    foreign = ['binary_package', 'source_package']

orm.mapper(PackageFile, t_package_files, properties={
    'binary_package' : orm.relation(BinaryPackage,
        backref=backref('package_files', cascade='all, delete-orphan')),
    'source_package' : orm.relation(SourcePackage,
        backref=backref('package_files', cascade='all, delete-orphan')),
})

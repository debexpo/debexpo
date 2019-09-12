# -*- coding: utf-8 -*-
#
#   user_countries.py — user_counties table model
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
Holds user_countries table model.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import sqlalchemy as sa
from sqlalchemy import orm

import xml.dom.minidom

import logging

from debexpo.model import meta, OrmObject

t_user_countries = sa.Table(
    'user_countries', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('name', sa.types.String(100), nullable=False),
    )


class UserCountry(OrmObject):
    pass


def create_iso_countries():
    parsed = xml.dom.minidom.parse(
        open('/usr/share/xml/iso-codes/iso_3166.xml'))
    entries = parsed.getElementsByTagName('iso_3166_entry')
    for entry in entries:
        if entry.attributes.get('common_name') is not None:
            value = entry.attributes['common_name'].value
        else:
            value = entry.attributes['name'].value
        add_country(value, commit=False)
    meta.session.commit()


def add_country(name, commit=True):
    query = meta.session.query(UserCountry)
    if query.filter_by(name=name).count():
        return

    logging.info(u"Adding country: %s", name)
    c = UserCountry(name=name)
    meta.session.add(c)
    if commit:
        meta.session.commit()


orm.mapper(UserCountry, t_user_countries)

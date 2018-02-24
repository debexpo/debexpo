# -*- coding: utf-8 -*-
#
#   data_store.py - Generic, general purpose data store
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2011 Arno Töll <debian@toell.net>
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
Holds data_store model
"""

__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2011 Arno Töll'
__license__ = 'MIT'

import sqlalchemy as sa
from sqlalchemy import orm

import logging

from debexpo.model import meta, OrmObject

t_user_countries = sa.Table('data_store', meta.metadata,
    sa.Column('namespace', sa.types.String(100), primary_key=True),
    sa.Column('code', sa.types.String(100), primary_key=True, nullable=False),
    sa.Column('value', sa.types.String(100), nullable=True)
    )

class DataStore(OrmObject):
    pass

orm.mapper(DataStore, t_user_countries)


def fill_data_store():
    import debexpo.model.data.data_store_init
    import logging
    for data in debexpo.model.data.data_store_init.DATA_STORE_INIT_OBJECTS:
        query = meta.session.query(DataStore).filter(DataStore.code == data.code).filter(DataStore.namespace == data.namespace).count()
        if (query):
            continue
        logging.info("Pre-configure value %s.%s" % (data.namespace, data.code))
        meta.session.add(data)
    meta.session.commit()



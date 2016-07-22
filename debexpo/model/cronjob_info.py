# -*- coding: utf-8 -*-
#
#   cronjob_info.py — cronjob_info table model
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2016 Kentaro Hayshi <kenhys@gmail.com>
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
Holds cronjob_info table model.
"""

__author__ = 'Kentaro Hayashi'
__copyright__ = 'Copyright © 2016 Kentaro Hayashi'
__license__ = 'MIT'

import json
import os

from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException

from pylons import config

import sqlalchemy as sa
from sqlalchemy import orm

import debexpo.lib

from debexpo.model import meta, OrmObject

t_cronjob_info = sa.Table('cronjob_info', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('name', sa.types.Text(), nullable=False),
    sa.Column('schedule', sa.types.Integer, nullable=False),
    sa.Column('last_run', sa.types.DateTime, nullable=False),
    )

class CronJobInfo(OrmObject):
    pass

orm.mapper(CronJobInfo, t_cronjob_info)

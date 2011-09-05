# -*- coding: utf-8 -*-
#
#   sponsor_metrics.py — rudimentary model for sponsor metrics
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
Holds Sponsor Metrics Model
"""

__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2011 Arno Töll'
__license__ = 'MIT'

import os
import datetime

import sqlalchemy as sa
from sqlalchemy import orm

from debexpo.model import meta, OrmObject
from debexpo.model.users import User
from debexpo.lib import constants
import debexpo.lib.utils

t_sponsor_metrics = sa.Table(
    'sponsor_metrics', meta.metadata,
    sa.Column('user_id', sa.types.Integer, sa.ForeignKey('users.id'), primary_key=True),
    sa.Column('availability', sa.types.Integer, nullable=False),
    sa.Column('contact', sa.types.Integer, nullable=False),
    sa.Column('types', sa.types.Text, nullable=True),
    sa.Column('guidelines', sa.types.Integer, nullable=True),
    sa.Column('guidelines_text', sa.types.Text, nullable=True),
    sa.Column('technical_requirements', sa.types.Text, nullable=True),
    sa.Column('social_requirements', sa.types.Text, nullable=True)
    )

class SponsorMetrics(OrmObject):
    foreign = ['user']

    def technical_requirements_to_database(self, requirements):
        """
        Takes a list of technical requirements and converts them in
        the internal database representation which is a bit map.
        The internal structure is considered an implementation detail

        ```requirements``` A list of SPONSOR_TECHNICAL_REQUIREMENTS which shall
            be stored in this object
        """
        indexed_requirements = [y for x,y in constants.SPONSOR_TECHNICAL_REQUIREMENTS]
        for i in indexed_requirements:
            if i in requirements:
                indexed_requirements[indexed_requirements.index(i)] = '1'
            else:
                indexed_requirements[indexed_requirements.index(i)] = '0'
        self.technical_requirements = ''.join(indexed_requirements)

    def database_to_technical_requirements(self):
        """
        Returns a list of SPONSOR_TECHNICAL_REQUIREMENTS which have been stored
        in the database object
        """
        if not self.technical_requirements:
            return (None, )
        requirements = []
        i = 0
        indexed_requirements = [y for x,y in constants.SPONSOR_TECHNICAL_REQUIREMENTS]
        for numreq in self.technical_requirements:
            if numreq == '1':
                 requirements.append(indexed_requirements[i])
            i += 1
        return requirements

    def get_guidelines(self):
        """
        Return a formatted and sanitized string of the guidelines the sponsor
        configured
        """

        if self.guidelines == constants.SPONSOR_GUIDELINES_TYPE_TEXT:
            s = self.guidelines_text
            s = s.replace('<', '&lt;')
            s = s.replace('>', '&gt;')
            s = s.replace('\n', '<br />')
            return s
        elif self.guidelines == constants.SPONSOR_GUIDELINES_TYPE_URL:
            return "<a href=\"%s\">%s</a>" % (self.guidelines_text, self.guidelines_text)
        else:
            return "None"

    def get_social_requirements(self):
        """
        Return a formatted and sanitized string of the social requirements the sponsor
        configured
        """

        if self.social_requirements:
            s = self.social_requirements
            s = s.replace('<', '&lt;')
            s = s.replace('>', '&gt;')
            s = s.replace('\n', '<br />')
            return s
        else:
            return "None"

    def allowed(self, flag):
        """
        Returns true if the user associated with this object allowed to display a
        contact address. This method also honors the SPONSOR_METRICS_RESTRICTED flag

        ```flag``` A SPONSOR_CONTACT_METHOD_* flag which should be checked
        """
        if self.availability == constants.SPONSOR_METRICS_RESTRICTED and self.contact == flag:
            return True
        elif self.availability == constants.SPONSOR_METRICS_PUBLIC:
            return True
        return False


orm.mapper(SponsorMetrics, t_sponsor_metrics, properties={
    'user' : orm.relation(User, backref='sponsor_metrics')
})

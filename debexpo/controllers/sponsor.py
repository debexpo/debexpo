# -*- coding: utf-8 -*-
#
#   index.py — index controller
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
Holds the IndexController.
"""

__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2011 Arno Töll'
__license__ = 'MIT'

import logging

from debexpo.lib.base import BaseController, c, config, render, session, \
    redirect, url, abort
from debexpo.lib import constants
from debexpo.model.sponsor_metrics import SponsorMetrics, SponsorTags, SponsorMetricsTags
from debexpo.model.users import User

from sqlalchemy.orm import joinedload, contains_eager

from debexpo.model import meta

log = logging.getLogger(__name__)

class SponsorController(BaseController):

    def clear(self):
        """
        Clear applied filters in the session.
        This method can be safely called, even if no filter was registered
        """

        if 'sponsor_filters' in session:
            log.debug("Clear sponsor filter")
            del(session['sponsor_filters'])
            session.save()

        redirect(url('sponsors'))


    def toggle(self, tag):
        """
        Toggle a filter within the session.
        This method prepares a list of filters to limit results in the sponsor list

        ```tag``` the sponsor tag to be filtered. If the tag is already in the filter
            list remove it, add it otherwise.
        """

        if tag not in [x.tag for x in meta.session.query(SponsorTags).all()]:
            abort(404)

        if 'sponsor_filters' not in session:
            session['sponsor_filters'] = []

        if tag in session['sponsor_filters']:
            log.debug("Removing tag %s from the filter list" % (tag))
            session['sponsor_filters'].remove(tag)
        else:
            log.debug("Adding tag %s to the filter list" % (tag))
            session['sponsor_filters'].append(tag)
        session.save()

        redirect(url('sponsors'))

    def index(self):
        """
        Return an introduction page for sponsors
        This page honors filters configured in the user session
        """

        if not config['debexpo.enable_experimental_code'].lower() == 'true':
            return render('/sponsor/index-old.mako')

        if 'debexpo.html.sponsors_intro' in config:
            f = open(config['debexpo.html.sponsors_intro'])
            c.custom_html = literal(f.read())
            f.close()
        else:
            c.custom_html = ''
        c.constants = constants

        c.sponsors = meta.session.query(SponsorMetrics)\
            .options(joinedload(SponsorMetrics.user))\
            .options(joinedload(SponsorMetrics.tags))\
            .filter(SponsorMetrics.availability >= constants.SPONSOR_METRICS_RESTRICTED)\
            .all()

        # The select above works fine, except that it sucks.
        # It suffers from a poor performance and it could be significantly improved by querying the tag
        # labels and descriptions (i.e. the SponsorTags table by joining them with SponsorMetricsTags.
        # However the resulting result set does not quite look like what I imagine. Feel free to replace it
        # by something which actually works.

        #c.sponsors = meta.session.query(SponsorMetrics, SponsorMetricsTags, SponsorTags, User)\
        #    .join(User)\
        #    .join(SponsorMetricsTags)\
        #    .join(SponsorTags)\
        #    .filter(SponsorMetrics.availability >= constants.SPONSOR_METRICS_RESTRICTED)\


        if 'sponsor_filters' in session:
            log.debug("Applying tag filter")
            c.sponsor_filter = session['sponsor_filters']
        else:
            c.sponsor_filter = []

        c.technical_tags = meta.session.query(SponsorTags).filter_by(tag_type=constants.SPONSOR_METRICS_TYPE_TECHNICAL).all()
        c.social_tags = meta.session.query(SponsorTags).filter_by(tag_type=constants.SPONSOR_METRICS_TYPE_SOCIAL).all()


        return render('/sponsor/index.mako')

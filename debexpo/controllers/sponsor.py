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
import random
import struct
import socket

from debexpo.lib.base import BaseController, c, config, render, session, \
    redirect, url, abort, request, SubMenu, _
from debexpo.lib import constants
from debexpo.model.sponsor_metrics import SponsorMetrics, SponsorTags, SponsorMetricsTags
from debexpo.model.users import User
from debexpo.model.user_countries import UserCountry
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion
from debexpo.model.package_comments import PackageComment
from debexpo.model.package_info import PackageInfo
from debexpo.model.source_packages import SourcePackage
from debexpo.model.binary_packages import BinaryPackage
from debexpo.model.package_files import PackageFile
from debexpo.model.package_subscriptions import PackageSubscription


from debexpo.lib.utils import get_package_dir


from sqlalchemy.orm import joinedload, contains_eager

from debexpo.model import meta

log = logging.getLogger(__name__)

class SponsorController(BaseController):

    def __init__(self):
        """
        Constructor, does nothing but to define the submenu
        """
        c.submenu = SubMenu()
        c.submenu.set_label("About Sponsoring")
        c.submenu.add_entry(_("Overview"), url("sponsors"))
        c.submenu.add_entry(_("Join a packaging team"), url("packaging-team"))
        c.submenu.add_entry(_("Sponsoring Guidelines"), url("guidelines"))
        c.submenu.add_entry(_("Request for Sponsorship"), url("rfs-howto"))
        BaseController.__init__(self)

    def _validate_tags(self, tags, existing_tags = None):
        """
        Validates a list of tags with actual existing ones

        ```tags```
            A list of tags which need to be verified

        ```existing_tags````
            The list of existing tags. Might be None to let this method fetch the tag list

        """

        if not existing_tags:
            existing_tags = [tag.tag for tag in meta.session.query(SponsorTags).all()]
        else:
            existing_tags = [tag.tag for tag in existing_tags]

        for tag in tags:
            if not tag in existing_tags:
                return False
        return True

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


    def save(self):
        """
        Toggle a filter within the session.
        This method prepares a list of filters to limit results in the sponsor list

        ```tag``` the sponsor tag to be filtered. If the tag is already in the filter
            list remove it, add it otherwise.
        """

        tags = request.params.getall('t')
        if not self._validate_tags(tags):
            abort(404)

        if 'sponsor_filters' not in session:
            session['sponsor_filters'] = []

        session['sponsor_filters'] = tags
        session.save()

        redirect(url('sponsors'))

    def guidelines(self):

        if not config['debexpo.enable_experimental_code'].lower() == 'true':
            return render('/sponsor/index-old.mako')

        c.constants = constants

        c.sponsors = meta.session.query(SponsorMetrics)\
            .options(joinedload(SponsorMetrics.user))\
            .options(joinedload(SponsorMetrics.tags))\
            .filter(SponsorMetrics.availability >= constants.SPONSOR_METRICS_RESTRICTED)\
            .all()

        def hash_ip():
            """
            This is a simple hashing algorithm not supposed to be called from anywhere
            but for internal use only.
            It reads the client IP address and returns a float between 0.01 and 0.91 which is
            used as input for random.shuffle
            """
            ip = request.environ['REMOTE_ADDR']
            try:
                ip = struct.unpack( "!L", socket.inet_pton( socket.AF_INET, ip ))
                ip = ip[0]
            except socket.error:
                ip = struct.unpack( "!QQ", socket.inet_pton( socket.AF_INET6, ip ))
                ip = ip[1]
            ip = (float(ip % 10) + 0.01) / 10
            return ip

        random.shuffle(c.sponsors, hash_ip)

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
        if request.params.getall('t'):
            c.sponsor_filter = request.params.getall('t')

        c.technical_tags = meta.session.query(SponsorTags).filter_by(tag_type=constants.SPONSOR_METRICS_TYPE_TECHNICAL).all()
        c.social_tags = meta.session.query(SponsorTags).filter_by(tag_type=constants.SPONSOR_METRICS_TYPE_SOCIAL).all()

        if not self._validate_tags(c.sponsor_filter, c.technical_tags + c.social_tags):
            abort(404)

        return render('/sponsor/guidelines.mako')

    def packaging_team(self):
        return render('/sponsor/packaging_team.mako')


    def rfs_howto(self, packagename = None):


        c.package = None
        c.package_dir = None
        if packagename:
            package = meta.session.query(Package).filter_by(name=packagename).first()
            if package:
                c.package = package
                c.package_dir = get_package_dir(package.name)

        return render('/sponsor/rfs_howto.mako')

    def index(self):
        """
        Return an introduction page for sponsors
        This page honors filters configured in the user session
        """

        if 'debexpo.html.sponsors_intro' in config:
            f = open(config['debexpo.html.sponsors_intro'])
            c.custom_html = literal(f.read())
            f.close()
        else:
            c.custom_html = ''

        return render('/sponsor/index.mako')


    def developer(self, id):
        if not config['debexpo.enable_experimental_code'].lower() == 'true':
            return render('/sponsor/index-old.mako')

        log.debug("Getting profile for user = %s" % (id))

        c.constants = constants

        c.sponsor = meta.session.query(SponsorMetrics)\
            .options(joinedload(SponsorMetrics.user))\
            .options(joinedload(SponsorMetrics.tags))\
            .filter(SponsorMetrics.availability >= constants.SPONSOR_METRICS_RESTRICTED)\
            .filter(User.email == id)\
            .first()
        if not c.sponsor:
            abort(404)
        c.profile = c.sponsor.user
        c.countries = { -1: '' }
        for country in meta.session.query(UserCountry).all():
            c.countries[country.id] = country.name


        return render('/sponsor/profile.mako')

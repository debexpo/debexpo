# -*- coding: utf-8 -*-
#
#   index.py — index controller
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
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
import json
import urllib

from debexpo.lib.base import BaseController, c, config, render, session, \
    redirect, url, abort, request, SubMenu, _
from debexpo.lib import constants
from debexpo.model.sponsor_metrics import SponsorMetrics, SponsorTags
from debexpo.model.users import User
from debexpo.model.user_countries import UserCountry
from debexpo.model.package_versions import PackageVersion
from debexpo.model.package_info import PackageInfo
from debexpo.model.packages import Package

# The following import are used in the template rfs_template
from debexpo.model.source_packages import SourcePackage  # NOQA
from debexpo.model.package_files import PackageFile  # NOQA

from debexpo.lib.utils import get_package_dir

from sqlalchemy.orm import joinedload

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
        # c.submenu.add_entry(_("Join a packaging team"), url("packaging-team"))
        c.submenu.add_entry(_("Sponsoring Guidelines"), url("guidelines"))
        c.submenu.add_entry(_("Request for Sponsorship"), url("rfs-howto"))
        BaseController.__init__(self)

    def _validate_tags(self, tags, existing_tags=None):
        """
        Validates a list of tags with actual existing ones

        ```tags```
            A list of tags which need to be verified

        ```existing_tags````
            The list of existing tags. Might be None to let this method fetch
            the tag list
        """

        if not existing_tags:
            existing_tags = [tag.tag for tag in meta.session.query(
                                 SponsorTags).all()]
        else:
            existing_tags = [tag.tag for tag in existing_tags]

        for tag in tags:
            if tag not in existing_tags:
                return False
        return True

    def _get_package_description(self, package_version):
        control = meta.session.query(PackageInfo) \
            .filter_by(package_version_id=package_version.id) \
            .filter_by(from_plugin='controlfields') \
            .first()

        if control:
            info = json.loads(control.data)

            if info:
                return info.get('Short-Description')

    def _get_package_rfs_info(self, package_version):
        info = None

        rfstemplate = meta.session.query(PackageInfo) \
            .filter_by(package_version_id=package_version.id) \
            .filter_by(from_plugin='rfstemplate') \
            .first()

        if rfstemplate:
            info = json.loads(rfstemplate.data)

        control_fields = meta.session.query(PackageInfo) \
            .filter_by(package_version_id=package_version.id) \
            .filter_by(from_plugin='controlfields') \
            .first()

        if rfstemplate and control_fields:
            fields = json.loads(control_fields.data)

            if 'Homepage' in fields:
                info['upstream-url'] = \
                        fields['Homepage']

            if 'Vcs-Browser' in fields:
                info['package-vcs'] = \
                        fields['Vcs-Browser']

        return info

    def _get_package_extra_info(self, package_version):
        category = []
        categories = None
        severity = None

        # Info from debianqa (NMU, QA, Team or normal upload)
        debianqa = meta.session.query(PackageInfo) \
            .filter_by(package_version_id=package_version.id) \
            .filter_by(from_plugin='debianqa') \
            .first()
        if debianqa:
            qadata = json.loads(debianqa.data)
            if 'nmu' in qadata and qadata['nmu']:
                category.append('NMU')
            if 'qa' in qadata and qadata['qa']:
                category.append('QA')
            if 'team' in qadata and qadata['team']:
                category.append('Team')
            if 'in-debian' in qadata and qadata['in-debian']:
                severity = 'normal'

        # Info from closedbugs (ITP, ITA or RC)
        closedbugs = meta.session.query(PackageInfo) \
            .filter_by(package_version_id=package_version.id) \
            .filter_by(from_plugin='closedbugs') \
            .first()

        if closedbugs:
            if 'ITP' in closedbugs.outcome:
                category.append('ITP')
                severity = 'wishlist'
            if 'RC' in closedbugs.outcome:
                category.append('RC')
                severity = 'important'
            if 'ITS' in closedbugs.outcome:
                category.append('ITS')
            if 'ITA' in closedbugs.outcome:
                category.append('ITA')

        if category:
            categories = '[{}]'.format(', '.join(category))

        return (categories, severity)

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
        This method prepares a list of filters to limit results in the sponsor
        list

        ```tag``` the sponsor tag to be filtered. If the tag is already in the
        filter list remove it, add it otherwise.
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
            .filter(SponsorMetrics.availability >=
                    constants.SPONSOR_METRICS_RESTRICTED)\
            .all()

        def hash_ip():
            """
            This is a simple hashing algorithm not supposed to be called from
            anywhere but for internal use only.
            It reads the client IP address and returns a float between 0.01 and
            0.91 which is used as input for random.shuffle
            """
            ip = request.environ['REMOTE_ADDR']
            try:
                ip = struct.unpack("!L", socket.inet_pton(socket.AF_INET, ip))
                ip = ip[0]
            except socket.error:
                ip = struct.unpack("!QQ", socket.inet_pton(socket.AF_INET6, ip))
                ip = ip[1]
            ip = (float(ip % 10) + 0.01) / 10
            return ip

        random.shuffle(c.sponsors, hash_ip)

        # The select above works fine, except that it sucks.
        # It suffers from a poor performance and it could be significantly
        # improved by querying the tag labels and descriptions (i.e. the
        # SponsorTags table by joining them with SponsorMetricsTags.
        # However the resulting result set does not quite look like what I
        # imagine. Feel free to replace it by something which actually works.

        # c.sponsors = meta.session.query(SponsorMetrics,
        #                                 SponsorMetricsTags, SponsorTags,
        #                                 User)\
        #     .join(User)\
        #     .join(SponsorMetricsTags)\
        #     .join(SponsorTags)\
        #     .filter(SponsorMetrics.availability >=
        #             constants.SPONSOR_METRICS_RESTRICTED).all()

        if 'sponsor_filters' in session:
            log.debug("Applying tag filter")
            c.sponsor_filter = session['sponsor_filters']
        else:
            c.sponsor_filter = []
        if request.params.getall('t'):
            c.sponsor_filter = request.params.getall('t')

        c.technical_tags = meta.session.query(SponsorTags) \
            .filter_by(tag_type=constants.SPONSOR_METRICS_TYPE_TECHNICAL) \
            .all()
        c.social_tags = meta.session.query(SponsorTags) \
            .filter_by(tag_type=constants.SPONSOR_METRICS_TYPE_SOCIAL) \
            .all()

        if not self._validate_tags(c.sponsor_filter,
                                   c.technical_tags + c.social_tags):
            abort(404)

        return render('/sponsor/guidelines.mako')

    def packaging_team(self):
        return render('/sponsor/packaging_team.mako')

    def rfs_howto(self, packagename=None):
        c.package = None
        c.package_dir = None
        c.rfstemplate = None
        c.category = None
        c.severity = None
        c.description = None

        if packagename:
            package = meta.session.query(Package) \
                .filter_by(name=packagename) \
                .first()

            if package:
                c.package = package
                c.package_dir = get_package_dir(package.name)

                latest = meta.session.query(PackageVersion) \
                    .filter_by(package_id=package.id) \
                    .order_by(PackageVersion.id.desc()) \
                    .first()

                if latest:
                    c.rfstemplate = self._get_package_rfs_info(latest)
                    (c.category, c.severity) = \
                        self._get_package_extra_info(latest)
                    c.description = self._get_package_description(latest)

        # This is a workaround for Thunderbird and some other clients
        # not handling properly '+' in the mailto body parameter.
        c.mailbody = render('/sponsor/rfs_template.mako')
        c.mailbody = urllib.quote_plus(c.mailbody.encode('utf-8')) \
            .replace('+', '%20')

        return render('/sponsor/rfs_howto.mako')

    def index(self):
        """
        Return an introduction page for sponsors
        This page honors filters configured in the user session
        """

        return render('/sponsor/index.mako')

    def developer(self, id):
        if not config['debexpo.enable_experimental_code'].lower() == 'true':
            return render('/sponsor/index-old.mako')

        log.debug("Getting profile for user = %s" % (id))

        c.constants = constants

        c.sponsor = meta.session.query(SponsorMetrics)\
            .options(joinedload(SponsorMetrics.user))\
            .options(joinedload(SponsorMetrics.tags))\
            .filter(SponsorMetrics.availability >=
                    constants.SPONSOR_METRICS_RESTRICTED)\
            .filter(User.email == id)\
            .first()
        if not c.sponsor:
            abort(404)
        c.profile = c.sponsor.user
        c.countries = {-1: ''}
        for country in meta.session.query(UserCountry).all():
            c.countries[country.id] = country.name

        return render('/sponsor/profile.mako')

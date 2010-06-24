# -*- coding: utf-8 -*-
#
#   packages.py — Packages controller
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
Holds the PackagesController class.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging
import apt_pkg
from sqlalchemy import exceptions
from pylons.i18n import get_lang

from debexpo.lib.base import *

from debexpo.model import meta
from debexpo.model.package_versions import PackageVersion
from debexpo.model.packages import Package
from debexpo.model.users import User
from debexpo.lib import constants

log = logging.getLogger(__name__)

class PackagesController(BaseController):

    def _get_packages(self, package_filter=None, package_version_filter=None):
        """
        Returns a list of packages that fit the filters.

        ``package_filter``
            An SQLAlchemy filter on the package.

        ``package_version_filter``
            An SQLAlchemy filter on the package.
        """
        # I want to use apt_pkg.CompareVersions later, so init() needs to be called.
        apt_pkg.init()

        log.debug('Getting package list')
        query = meta.session.query(Package)

        if package_filter is not None:
            log.debug('Applying package list filter')
            query = query.filter(package_filter)

        if package_version_filter is not None:
            log.debug('Applying package version list filter')
            query = query.filter(Package.id == PackageVersion.package_id)
            query = query.filter(package_version_filter)

        return query.all()

    def _get_user(self, email):
        return meta.session.query(User).filter_by(email=email).first()

    def index(self):
        """
        Entry point into the PackagesController.
        """
        log.debug('Main package listing requested')

        # List of packages to show in the list.
        packages = self._get_packages()

        # Render the page.
        c.config = config
        c.packages = packages
        c.feed_url = h.url_for('packages_feed')
        return render('/packages/index.mako')

    def feed(self, filter=None, id=None):
        feed = h.feedgenerator.Rss201rev2Feed(
            title=_('%s packages' % config['debexpo.sitename']),
            link=config['debexpo.server'] + h.url_for('packages'),
            description=_('A feed of packages on %s' % config['debexpo.sitename']),
            language=get_lang()[0])

        if filter == 'section':
            packages = self._get_packages(package_version_filter=(PackageVersion.section == id))

        elif filter == 'uploader':
            user = self._get_user(id)
            if user is not None:
                packages = self._get_packages(package_filter=(Package.user_id == user.id))
            else:
                packages = []

        elif filter == 'maintainer':
            packages = self._get_packages(package_version_filter=(PackageVersion.maintainer == id))

        else:
            packages = self._get_packages()

        for item in packages:
            desc = _('Package %s uploaded by %s.' % (item.name, item.user.name))

            desc += '<br/><br/>'

            if item.needs_sponsor:
                desc += _('Uploader is currently looking for a sponsor.')
            else:
                desc += _('Uploader is currently not looking for a sponsor.')

            desc += '<br/><br/>' + item.description.replace('\n', '<br/>')

            feed.add_item(title='%s %s' % (item.name, item.package_versions[-1].version),
                link=config['debexpo.server'] + h.url_for('package', packagename=item.name),
                description=desc, unique_id=str(item.package_versions[-1].id))

        return feed.writeString('utf-8')

    def section(self, id):
        """
        List of packages depending on section.
        """
        log.debug('Package listing on section = "%s" requested' % id)

        packages = self._get_packages(package_version_filter=(PackageVersion.section == id))

        c.config = config
        c.packages = packages
        c.section = id
        c.feed_url = h.url_for('packages_filter_feed', filter='section', id=id)
        return render('/packages/section.mako')

    def uploader(self, id):
        """
        List of packages depending on uploader.
        """
        log.debug('Package listing on user.email = "%s" requested' % id)

        user = self._get_user(id)

        if user is not None:
            packages = self._get_packages(package_filter=(Package.user_id == user.id))
            username = user.name
            email = user.email
        else:
            log.warning('Could not find user')
            packages = []
            username = id
            email = id

        c.config = config
        c.email = email
        c.packages = packages
        c.username = username
        c.feed_url = h.url_for('packages_filter_feed', filter='uploader', id=id)
        return render('/packages/uploader.mako')

    def my(self):
        """
        List of packages depending on current user logged in.
        """
        log.debug('Package listing on current user requested')

        if 'user_id' not in session:
            log.debug('Requires authentication')
            session['path_before_login'] = request.path_info
            session.save()
            redirect_to(h.url_for(controller='login'))

        details = meta.session.query(User).filter_by(id=session['user_id']).first()
        if not details:
            redirect_to(h.url_for(controller='logout'))

        return self.uploader(details.email)

    def maintainer(self, id):
        """
        List of packages depending on the Maintainer email address.
        """
        log.debug('Package listing on package_version.maintainer = "%s" requested', id)

        packages = self._get_packages(package_version_filter=(PackageVersion.maintainer == id))

        c.config = config
        c.packages = packages
        c.maintainer = id
        c.feed_url = h.url_for('packages_filter_feed', filter='maintainer', id=id)
        return render('/packages/maintainer.mako')

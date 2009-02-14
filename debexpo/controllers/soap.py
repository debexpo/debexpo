# -*- coding: utf-8 -*-
#
#   soap.py — soap controller
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
Holds the SOAP controller.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging

from debexpo.lib.base import *
from debexpo.controllers.packages import PackagesController

from debexpo.model.users import User
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion

from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.primitive import String, Array

log = logging.getLogger(__name__)

class DebexpoService(SimpleWSGISoapApp):

    def _get_packages(self, package_filter=None, package_version_filter=None, email=None):
        """
        Helper method to construct the list for package information.
        """
        pkg_ctl = PackagesController()

        if email is not None:
            user = pkg_ctl._get_user(email)
            if user is None:
                log.error('Could not find user; returning empty list')
                return []
            package_filter = (Package.user_id == user.id)

        packages = pkg_ctl._get_packages(package_filter=package_filter,
            package_version_filter=package_version_filter)

        out = []
        for item in packages:
            out.append([item.name, item.package_versions[-1].version,
                '%s <%s>' % (item.user.name, item.user.email),
                item.description,
                config['debexpo.server'] + h.url_for('package', packagename=item.name)])

        return out

    @soapmethod(String, _returns=Array(Array(String)))
    def uploader(self, email):
        """
        Return package list filtered on uploader.
        """
        log.debug('Getting packages filtered on uploader = %s' % email)
        return self._get_packages(email=email)

    @soapmethod(String, _returns=Array(Array(String)))
    def section(self, section):
        """
        Return package list filtered on section.
        """
        log.debug('Getting packages filtered on section = %s' % section)
        return self._get_packages(package_version_filter=(PackageVersion.section == section))

    @soapmethod(String, _returns=Array(Array(String)))
    def maintainer(self, email):
        """
        Return package list filtered on maintainer.
        """
        log.debug('Getting packages filtered on maintainer = %s' % email)
        return self._get_packages(package_version_filter=(PackageVersion.maintainer == email))

    @soapmethod(_returns=Array(Array(String)))
    def packages(self):
        """
        Return package list.
        """
        log.debug('Getting package list')
        return self._get_packages()

    @soapmethod(String, String, _returns=Array(String))
    def package(self, name, version):
        """
        Return details a specific package and version.
        """
        q = meta.session.query(Package).filter_by(name=name)
        q = q.filter(Package.id == PackageVersion.package_id)
        q = q.filter(PackageVersion.version == version)
        package = q.first()

        if package is None:
            return []

        r = meta.session.query(PackageVersion).filter_by(version=version)
        r = r.filter(PackageVersion.package_id == Package.id)
        r = r.filter(Package.name == name)
        package_version = r.first()

        if package_version is None:
            return []

        return [package.name,
            '%s <%s>' % (package.user.name, package.user.email),
            package.description,
            str(package.needs_sponsor),
            package_version.version,
            package_version.section,
            package_version.distribution,
            package_version.component,
            package_version.priority,
            package_version.closes,
            str(package_version.uploaded)]

    @soapmethod(String, _returns=Array(String))
    def versions(self, name):
        """
        Returns a list of package versions for a package.
        """
        q = meta.session.query(Package).filter_by(name=name)
        package = q.first()

        if package is None:
            return []

        return [pv.version for pv in package.package_versions]

SoapController = DebexpoService()

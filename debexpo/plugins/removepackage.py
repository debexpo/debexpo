# -*- coding: utf-8 -*-
#
#   removepackage.py — removepackage plugin
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
Holds the removepackage plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import apt_pkg
import logging

from debexpo.plugins import BasePlugin

from debexpo.model import meta
from debexpo.model.packages import Package

log = logging.getLogger(__name__)

class RemovePackagePlugin(BasePlugin):

    def test_remove_package(self):
        """
        Removes a package that has been uploaded to Debian.
        """
        source = self.changes['Source']
        log.debug('Checking whether package %s is in the repository' % source)

        package = meta.session.query(Package).filter_by(name=source).first()

        if package is None:
            # The package is not in the repository. This will happen the most often.
            log.debug('Package is not in the repository')
            return

        # Initialise apt_pkg
        apt_pkg.init()

        keep_package_versions = []
        for package_version in package.package_versions:
            if apt_pkg.version_compare(self.changes['Version'], package_version.version) < 0:
                keep_package_versions.append(package_version.version)

        if len(keep_package_versions) == 0:
            # Get rid of the whole package.
            self._remove_package_versions(package.package_versions)
            log.debug('Deleting package database entry: %s' % package.name)
            meta.session.delete(package)

        else:
            # Only remove certain package versions.
            for package_version in package.package_versions:
                if package_version not in keep_package_versions:
                    meta.session.delete(package_version)

        meta.session.commit()

plugin = RemovePackagePlugin

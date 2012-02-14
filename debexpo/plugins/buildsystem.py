# -*- coding: utf-8 -*-
#
#   buildsystem.py — buildsystem plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2012 Nicolas Dandrimont <nicolas.dandrimont@crans.org>
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
Holds the buildsystem plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = ', '.join([
        'Copyright © 2008 Jonny Lamb',
        'Copyright © 2010 Jan Dittberner',
        'Copyright © 2012 Nicolas Dandrimont',
        ])
__license__ = 'MIT'

import logging
import os

from debian import deb822

from debexpo.lib import constants
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)

class BuildSystemPlugin(BasePlugin):

    def test_build_system(self):
        """
        Finds the build system of the package.
        """
        log.debug('Finding the package\'s build system')

        dsc = deb822.Dsc(file(self.changes.get_dsc()))

        data = {}
        severity = constants.PLUGIN_SEVERITY_INFO

        build_depends = dsc.get('Build-Depends', '')

        if 'cdbs' in build_depends:
            outcome = "Package uses CDBS"
            data["build-system"] = "cdbs"
        elif 'debhelper' in build_depends:
            data["build-system"] = "debhelper"

            # Retrieve the debhelper compat level
            compatpath = os.path.join(self.tempdir, "extracted/debian/compat")
            try:
                with open(compatpath, "rb") as f:
                    compat_level = int(f.read().strip())
            except IOError:
                compat_level = None

            data["compat-level"] = compat_level

            # Warn on old compatibility levels
            if compat_level is None or compat_level <= 4:
                outcome = "Package uses debhelper with an old compatibility level"
                severity = constants.PLUGIN_SEVERITY_WARNING
            else:
                outcome = "Package uses debhelper"
        else:
            outcome = "Package uses an unknown build system"
            data["build-system"] = "unknown"
            severity = constants.PLUGIN_SEVERITY_WARNING

        self.failed(outcome, data, severity)


plugin = BuildSystemPlugin

#   buildsystem.py - buildsystem plugin
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2012 Nicolas Dandrimont <nicolas.dandrimont@crans.org>
#   Copyright © 2020 Baptiste Beauplat <lyknode@cilg.org>
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

import os
import re

from debexpo.plugins.models import BasePlugin, PluginSeverity


class PluginBuildSystem(BasePlugin):
    @property
    def name(self):
        return 'build-system'

    def run(self, changes, source):
        """
        Finds the build system of the package.
        """
        data = {}
        severity = PluginSeverity.info
        build_depends = changes.dsc.build_depends

        if 'cdbs' in build_depends:
            outcome = 'Package uses CDBS'
            data['build_system'] = 'cdbs'

        elif 'debhelper-compat' in build_depends:
            data['build_system'] = 'debhelper'
            outcome = 'Package uses debhelper-compat'

            matches = re.search(r'\bdebhelper-compat\s+\(=\s*(\d+)\)',
                                build_depends)
            if matches:
                compat_level = int(matches.group(1))
            else:
                compat_level = None

            data['compat_level'] = compat_level

        elif 'debhelper' in build_depends:
            data['build_system'] = 'debhelper'
            outcome = 'Package uses debhelper'

            # Retrieve the debhelper compat level
            compatpath = os.path.join(source.get_source_dir(),
                                      'debian', 'compat')
            try:
                with open(compatpath, 'rb') as f:
                    compat_level = int(f.read().strip())
            except IOError:
                compat_level = None

            data['compat_level'] = compat_level

        else:
            outcome = 'Package uses an unknown build system'
            data['build_system'] = 'unknown'
            severity = PluginSeverity.warning

        if data['build_system'] == 'debhelper':
            # Warn on old compatibility levels
            if compat_level is None or compat_level < 9:
                outcome += ' with an old compatibility level'
                severity = PluginSeverity.warning

        self.add_result('build_system', outcome, data, severity)

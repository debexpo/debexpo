#   native.py - native QA plugin
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2012 Nicolas Dandrimont <Nicolas.Dandrimont@crans.org>
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

from os.path import join

from debexpo.plugins.models import BasePlugin, PluginSeverity


class PluginNative(BasePlugin):
    @property
    def name(self):
        return 'native'

    def _get_source_format(self, source):
        try:
            with open(join(source.get_source_dir(), 'debian', 'source',
                           'format')) as source_format_file:
                source_format = source_format_file.readline()
        except IOError:
            source_format = '1.0 (no format file)'

        return source_format.rstrip('\n')

    def run(self, changes, source):
        """
        Test to see whether the package is a native package.
        """
        version = changes.dsc.version
        source_format = self._get_source_format(source)

        if not version.debian_revision:
            # Most uploads will not be native, and especially on mentors, a
            # native package is almost probably in error.
            self.add_result('native', 'Package is native',
                            {'format': source_format},
                            PluginSeverity.warning)
        else:
            self.add_result('native', 'Package is not native',
                            {'format': source_format},
                            PluginSeverity.info)

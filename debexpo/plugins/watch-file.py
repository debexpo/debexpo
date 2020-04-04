#   watchfile.py - watchfile plugin
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2012 Nicolas Dandrimont <Nicolas.Dandrimont@crans.org>
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from subprocess import check_output, CalledProcessError, STDOUT
import os
from re import search, MULTILINE

from debexpo.plugins.models import BasePlugin, PluginSeverity


class PluginWatchFile(BasePlugin):
    @property
    def name(self):
        return 'watch-file'

    def _watch_file_present(self, source):
        return os.path.isfile(os.path.join(source.get_source_dir(),
                                           'debian', 'watch'))

    def _run_uscan(self, source):
        try:
            self.output = check_output(["uscan", "--verbose", '--report'],
                                       stderr=STDOUT,
                                       cwd=source.get_source_dir(),
                                       text=True)
        except FileNotFoundError:  # pragma: no cover
            self.failed('uscan not found')
        except CalledProcessError as e:
            self.status = e.returncode
            self.output = e.output

    def _watch_file_works(self, source):
        self._run_uscan(source)
        return 'Newest version' in self.output

    def _extract_upstream_info(self):
        extract = r'(Newest version.*)\n.*\n(.*)\n'
        matches = search(extract, self.output, MULTILINE)

        if matches:
            return '\n'.join([matches[1], matches[2]])

    def run(self, changes, source):
        """
        Run the watch file-related checks in the package
        """

        self.status = 0
        self.output = ''
        data = {}

        if not self._watch_file_present(source):
            self.add_result('uscan', 'Watch file is not present', data,
                            PluginSeverity.warning)
            return

        if not self._watch_file_works(source):
            data['details'] = self.output
            self.add_result('uscan',
                            "A watch file is present but doesn't work", data,
                            PluginSeverity.warning)
            return

        if self.status == 1:
            self.add_result('uscan',
                            'Package is the latest upstream version', data,
                            PluginSeverity.info)
        else:
            data['details'] = self._extract_upstream_info()
            self.add_result('uscan', 'Newer upstream version available', data,
                            PluginSeverity.warning)

#   watchfile.py - watchfile plugin
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

from subprocess import TimeoutExpired, CalledProcessError
import os
from xml.etree import ElementTree

from debexpo.plugins.models import BasePlugin, PluginSeverity
from debexpo.tools.proc import debexpo_exec


class PluginWatchFile(BasePlugin):
    @property
    def name(self):
        return 'watch-file'

    def _watch_file_present(self, source):
        return os.path.isfile(os.path.join(source.get_source_dir(),
                                           'debian', 'watch'))

    def _run_uscan(self, source):
        try:
            output = debexpo_exec("uscan", ["--dehs", '--report'],
                                  cwd=source.get_source_dir(),
                                  text=True)
        except FileNotFoundError:  # pragma: no cover
            self.failed('uscan not found')
        except CalledProcessError as e:
            self.status = e.returncode
            output = e.output
        except TimeoutExpired:
            self.failed('uscan: timeout')

        return output

    def _parse_xml_uscan(self, output):
        root = ElementTree.fromstring(output)
        status = root.findtext('status')

        for key, tag in (('local', 'debian-uversion',),
                         ('upstream', 'upstream-version',),
                         ('url', 'upstream-url',),
                         ('warnings', 'warnings',),
                         ('errors', 'errors',),):
            values = root.findall(tag)

            for value in values:
                if self.data.get(key):
                    self.data[key] = '\n'.join([self.data[key],
                                               value.text])
                else:
                    self.data[key] = value.text

        return status

    def _watch_file_works(self, source):
        output = self._run_uscan(source)

        try:
            status = self._parse_xml_uscan(output)
        # This is there is case uscan could not format correctly its xml.
        # As this is not supposed to happen, is it excluded from testing
        except ElementTree.ParseError as e:  # pragma: no cover
            self.failed(f'failed to parse uscan output: {str(e)}')

        return status

    def run(self, changes, source):
        """
        Run the watch file-related checks in the package
        """

        self.status = 0
        self.data = {}

        if not self._watch_file_present(source):
            self.add_result('uscan', 'Watch file is not present', self.data,
                            PluginSeverity.warning)
            return

        if not self._watch_file_works(source):
            self.add_result('uscan',
                            "A watch file is present but doesn't work",
                            self.data, PluginSeverity.warning)
            return

        if self.status == 1:
            self.add_result('uscan',
                            'Package is the latest upstream version', self.data,
                            PluginSeverity.info)
        else:
            self.add_result('uscan', 'Newer upstream version available',
                            self.data, PluginSeverity.warning)

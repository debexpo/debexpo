#   diffclean.py - diffclean plugin
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
from os.path import dirname

from debexpo.plugins.models import BasePlugin, PluginSeverity
from debexpo.tools.proc import debexpo_exec


class PluginDiffClean(BasePlugin):
    @property
    def name(self):
        return 'diff-clean'

    def _run_diffstat(self, diff_file):
        try:
            output = debexpo_exec("diffstat", ["-p1", diff_file],
                                  cwd=dirname(diff_file))
        except FileNotFoundError:  # pragma: no cover
            self.failed('diffstat not found')
        # Looking at diffstat code, it only exit with a return code different
        # from 0 either if it fails to allocate memory or if there is a problem
        # with the options.
        # Excluded from testing.
        except CalledProcessError as e:  # pragma: no cover
            self.failed(f'diffstat failed: {e.stderr}')
        except TimeoutExpired:
            self.failed('diffstat: timeout')

        return output

    def run(self, changes, source):
        """
        Check to make sure the diff.gz is clean.
        """
        diff_file = changes.files.find(r'\.diff\.gz$')

        if diff_file is None:
            return

        diff_stat = self._run_diffstat(diff_file)

        data = {
            "modified_files": [],
        }

        # Last line is the summary line
        for item in diff_stat.splitlines()[:-1]:
            filename, stats = [i.strip() for i in item.split("|")]
            if not filename.startswith('debian/'):
                data["modified_files"].append((filename, stats))

        if not data["modified_files"]:
            self.add_result('diff-stat',
                            "The package's .diff.gz does not modify files"
                            " outside of debian/", data, PluginSeverity.info)
        else:
            self.add_result('diff-stat',
                            "The package's .diff.gz modifies files outside of "
                            "debian/", data, PluginSeverity.warning)

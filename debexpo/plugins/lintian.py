#   lintian.py - lintian plugin
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

from bisect import insort
from os.path import dirname
from collections import defaultdict
from subprocess import CalledProcessError, TimeoutExpired

from debexpo.plugins.models import BasePlugin, PluginSeverity
from debexpo.tools.proc import debexpo_exec


class PluginLintian(BasePlugin):
    levels = {
        'X': {'name': 'Experimental', 'severity': PluginSeverity.info,
              'outcome': 'Package has lintian experimental tags'},
        'P': {'name': 'Pedantic', 'severity': PluginSeverity.info,
              'outcome': 'Package has lintian pedantic tags'},
        'O': {'name': 'Override', 'severity': PluginSeverity.info,
              'outcome': 'Package has overridden lintian tags'},
        'I': {'name': 'Info', 'severity': PluginSeverity.info,
              'outcome': 'Package has lintian informational tags'},
        'W': {'name': 'Warning', 'severity': PluginSeverity.warning,
              'outcome': 'Package has lintian warnings'},
        'E': {'name': 'Error', 'severity': PluginSeverity.error,
              'outcome': 'Package has lintian errors'},
    }

    @property
    def name(self):
        return 'lintian'

    def _run_lintian(self, changes, source):
        try:
            output = debexpo_exec("lintian",
                                  ["-E",
                                   "-I",
                                   "--pedantic",
                                   "--show-overrides",
                                   # To avoid warnings in the testsuite when
                                   # run as root in CI.
                                   "--allow-root",
                                   "--fail-on", "none",
                                   str(changes)],
                                  cwd=dirname(changes.filename))
        except FileNotFoundError:  # pragma: no cover
            self.failed('lintian not found')
        except TimeoutExpired:
            self.failed('lintian took too much time to run')
        except CalledProcessError as e:
            self.failed(f'lintian failed to run: {e.stderr}')

        return output.split('\n')

    def run(self, changes, source):
        tags = self._run_lintian(changes, source)

        # Yes, three levels of defaultdict and one of list...
        def defaultdict_defaultdict_list():
            def defaultdict_list():
                return defaultdict(list)
            return defaultdict(defaultdict_list)

        lintian_warnings = defaultdict(defaultdict_defaultdict_list)
        lintian_severities = set()
        override_comments = []

        for tag in tags:
            if not tag:
                continue

            # lintian output is of the form """SEVERITY: package: lintian_tag
            # [lintian tag arguments]""" or """N: Override comment"""
            if tag.startswith("N: "):
                override_comments.append(tag[3:].strip())
                continue

            # Skip mask severity
            if tag.startswith("M: "):
                # Drop associated N:
                override_comments = []
                continue

            severity, package, rest = tag.split(': ', 2)
            lintian_severities.add(severity)
            lintian_tag_data = rest.split()
            lintian_tag = lintian_tag_data[0]
            lintian_data = ' '.join(lintian_tag_data[1:])
            severity = f'{severity}-{self.levels[severity]["name"]}'

            if override_comments:
                comments = ' '.join(override_comments)
                lintian_data += f' (override comment: {comments})'
                override_comments = []

            insort(lintian_warnings[package][severity][lintian_tag],
                   lintian_data)

        lintian_warnings = dict(sorted(lintian_warnings.items()))
        severity = PluginSeverity.info
        outcome = 'Package is lintian clean'

        for name, level in self.levels.items():
            if name in lintian_severities:
                severity = level['severity']
                outcome = level['outcome']

        self.add_result('lintian-tags', outcome, lintian_warnings,
                        severity)

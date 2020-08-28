#   closedbugs.py - closedbugs plugin
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#               2011 Arno Töll <debian@toell.net>
#               2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from collections import defaultdict

from django.conf import settings

from debexpo.bugs.models import BugType, BugSeverity, BugStatus
from debexpo.plugins.models import BasePlugin, PluginSeverity


class PluginClosedBugs(BasePlugin):
    @property
    def name(self):
        return 'closed-bugs'

    def run(self, changes, source):
        """
        Check to make sure the bugs closed belong to the package.
        """

        if not changes.closes:
            return

        bugs = [int(x) for x in changes.closes.split()]
        data = {
            'buglist': bugs,
            'errors': [],
            'bugs': defaultdict(list),
            }
        bugtypes = []
        has_rc = set()
        severity = PluginSeverity.info

        for bug in bugs:
            bug_info = None

            # Try to find bug info
            for item in changes.get_bugs():
                if item.number == bug:
                    bug_info = item
                    break

            # No bug found, let mark it as an error and skip it
            if not bug_info:
                data['errors'].append(f'Bug #{bug} does not exist')
                severity = PluginSeverity.error
                continue

            # Crunch info to display in the template
            packages = bug_info.packages.values_list('name', flat=True)
            sources = bug_info.sources.values_list('name', flat=True)
            info = f'{BugSeverity(bug_info.severity).label}'

            if bug_info.bugtype != BugType.bug:
                bugtypes.append(bug_info.bugtype)
                info += f', {BugType(bug_info.bugtype)._name_}'

            for package in packages:
                data['bugs'][package].append(
                    (bug_info.number, bug_info.subject, info))

            has_rc.add(bug_info.is_rc())

            # QA checks on the bug
            # 1. The bug belong to the package
            if not (changes.source in sources):
                data['errors'].append(f'Bug #{bug} does not belong to this '
                                      'package')
                severity = PluginSeverity.error

            # 2. The bug is open
            if bug_info.status == BugStatus.done and \
                    settings.BUGS_REPORT_NOT_OPEN:
                data['errors'].append(f'Bug #{bug} is closed')
                severity = PluginSeverity.error

            # 3. The bug is not an RFS, O or RFH
            if bug_info.bugtype in (BugType.RFS, BugType.O, BugType.RFH):
                severity = PluginSeverity.error
                data['errors'].append(
                    f'Bug #{bug} is a {BugType(bug_info.bugtype)._name_} bug')

        if severity != PluginSeverity.info:
            outcome = 'Package closes bugs in a wrong way'

        # 4. The upload don't closes multiple wnpp bugs
        elif len(bugtypes) > 1:
            severity = PluginSeverity.warning
            outcome = 'Package closes multiple wnpp bugs: ' \
                      f'{self._format_bug_types(bugtypes)}'

        else:
            bugtypes = self._format_bug_types(set(bugtypes), has_rc)

            if bugtypes:
                outcome = f'Package closes {bugtypes} bug'

            else:
                outcome = 'Package closes bug'

            if len(bugs) > 1:
                outcome += 's'

        self.add_result('bugs', outcome, data, severity)

    def _format_bug_types(self, bugtypes, has_rc=None):
        bugtypes = [BugType(bugtype)._name_ for bugtype in bugtypes]

        if has_rc and True in has_rc:
            bugtypes.append('RC')

        return ', '.join(bugtypes)

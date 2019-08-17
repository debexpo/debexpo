# -*- coding: utf-8 -*-
#
#   closedbugs.py — closedbugs plugin
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#               2011 Arno Töll <debian@toell.net>
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
Holds the closedbugs plugin.
"""

__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2011 Arno Töll'
__license__ = 'MIT'

from collections import defaultdict
import logging

from debexpo.lib import constants
from debexpo.plugins import BasePlugin
import SOAPpy

log = logging.getLogger(__name__)


class ClosedBugsPlugin(BasePlugin):
    URL = "http://bugs.debian.org/cgi-bin/soap.cgi"
    NS = "Debbugs/SOAP"

    def test_closed_bugs(self):
        """
        Check to make sure the bugs closed belong to the package.
        """

        if 'Closes' not in self.changes:
            log.debug('Package does not close any bugs')
            return

        log.debug('Checking whether the bugs closed in the package belong to '
                  'the package')

        bugs = [int(x) for x in self.changes['Closes'].split()]

        if bugs:
            log.debug('Creating SOAP proxy to bugs.debian.org')
            try:
                server = SOAPpy.SOAPProxy(self.URL, self.NS,
                                          simplify_objects=1)
                bugs_retrieved = server.get_status(*bugs)
                if 'item' in bugs_retrieved:
                    bugs_retrieved = bugs_retrieved['item']
                else:
                    bugs_retrieved = []
                # Force argument to be a list, SOAPpy returns a dictionary
                # instead of a dictionary list if only one bug was found
                if not isinstance(bugs_retrieved, list):
                    bugs_retrieved = [bugs_retrieved]
            except Exception as e:
                log.critical('An error occurred when creating the SOAP proxy '
                             'at "%s" (ns: "%s"): %s'
                             % (self.URL, self.NS, e))
                return

            data = {
                'buglist': bugs,
                'raw': {},
                'errors': [],
                'bugs': defaultdict(list),
                }

            # Index bugs retrieved
            for bug in bugs_retrieved:
                if 'key' in bug and 'value' in bug:
                    data["raw"][int(bug['key'])] = bug['value']
                else:
                    continue

            severity = constants.PLUGIN_SEVERITY_INFO
            closes_rc = False

            for bug in bugs:
                if bug not in data['raw']:
                    data["errors"].append('Bug #%s does not exist' % bug)
                    log.debug('{}'.format(data["errors"][-1]))
                    severity = max(severity, constants.PLUGIN_SEVERITY_ERROR)
                    continue

                name = data["raw"][bug]['package']
                data["bugs"][name].append((bug, data["raw"][bug]["subject"],
                                           data["raw"][bug]["severity"]))
                log.debug('Changes closes #{}: '
                          '{}'.format(bug, data["raw"][bug]["subject"]))

                if not (self.changes["Source"] in
                        data["raw"][bug]['source'].split(', ') or
                        name == "wnpp"):
                    data["errors"].append('Bug #%s does not belong to this '
                                          'package' % bug)
                    severity = max(severity, constants.PLUGIN_SEVERITY_ERROR)

                rc_severities = ['grave', 'serious', 'critical']
                if any(data["raw"][bug]["severity"] == severity for severity in
                        rc_severities):
                    closes_rc = True

            if severity != constants.PLUGIN_SEVERITY_INFO:
                outcome = "Package closes bugs in a wrong way"
            elif "wnpp" in data["bugs"] and len(data["bugs"]) == 1:
                if data['bugs']['wnpp'][0][1].startswith('ITP'):
                    outcome = "Package closes a ITP bug"
                elif data['bugs']['wnpp'][0][1].startswith('ITA'):
                    outcome = "Package closes a ITA bug"
                else:
                    outcome = "Package closes a WNPP bug"
            elif closes_rc:
                outcome = "Package closes a RC bug"
            else:
                outcome = "Package closes bug%s" % \
                    ("s" if len(bugs) > 1 else "")

            self.failed(outcome, data, severity)

        else:
            log.debug('Package does not close any bugs')

    def _package_in_descriptions(self, name, list):
        """
        Finds out whether a binary package is in a source package by looking at
        the Description field of the changes file for the binary package name.

        ``name``
            Name of the binary package.

        ``list``
            List of Description fields split by '\n'.
        """
        for item in list:
            if item.startswith(name + ' '):
                return True

        return False


plugin = ClosedBugsPlugin

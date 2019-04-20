# -*- coding: utf-8 -*-
#
#   lintian.py — lintian plugin
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2012 Nicolas Dandrimont <Nicolas.Dandrimont@crans.org>
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
Holds the lintian plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = ', '.join([
        'Copyright © 2008 Jonny Lamb',
        'Copyright © 2012 Nicolas Dandrimont',
        ])
__license__ = 'MIT'

from collections import defaultdict
import subprocess
import logging

from debexpo.lib import constants
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)


class LintianPlugin(BasePlugin):

    def test_lintian(self):
        """
        Method to run lintian on the package.
        """
        log.debug('Running lintian on the package')

        output = subprocess.Popen(["lintian",
                                   "-E",
                                   "-I",
                                   "--pedantic",
                                   "--show-overrides",
                                   # To avoid warnings in the testsuite when
                                   # run as root in CI.
                                   "--allow-root",
                                   self.changes_file],
                                  stdout=subprocess.PIPE).communicate()[0]

        items = output.split('\n')

        # Yes, three levels of defaultdict and one of list...
        def defaultdict_defaultdict_list():
            def defaultdict_list():
                return defaultdict(list)
            return defaultdict(defaultdict_list)
        lintian_warnings = defaultdict(defaultdict_defaultdict_list)

        lintian_severities = set()

        override_comments = []

        for item in items:
            if not item:
                continue

            # lintian output is of the form """SEVERITY: package: lintian_tag
            # [lintian tag arguments]""" or """N: Override comment"""
            if item.startswith("N: "):
                override_comments.append(item[3:].strip())
                continue
            severity, package, rest = item.split(': ', 2)
            lintian_severities.add(severity)
            lintian_tag_data = rest.split()
            lintian_tag = lintian_tag_data[0]
            lintian_data = lintian_tag_data[1:]
            if override_comments:
                lintian_data.append("(override comment: " +
                                    " ".join(override_comments) + ")")
                override_comments = []
            lintian_warnings[package][severity][lintian_tag] \
                .append(lintian_data)

        severity = constants.PLUGIN_SEVERITY_INFO
        if 'E' in lintian_severities:
            severity = constants.PLUGIN_SEVERITY_ERROR
            outcome = 'Package has lintian errors'
        elif 'W' in lintian_severities:
            severity = constants.PLUGIN_SEVERITY_WARNING
            outcome = 'Package has lintian warnings'
        elif 'I' in lintian_severities:
            outcome = 'Package has lintian informational warnings'
        elif 'O' in lintian_severities:
            outcome = 'Package has overridden lintian tags'
        elif 'P' in lintian_severities or 'X' in lintian_severities:
            outcome = 'Package has lintian pedantic/experimental warnings'
        else:
            outcome = 'Package is lintian clean'

        self.failed(outcome, lintian_warnings, severity)


plugin = LintianPlugin

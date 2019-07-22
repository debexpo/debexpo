# -*- coding: utf-8 -*-
#
#   rfstemplate.py - collect information for RFS template plugin
#
#   Copyright © 2016 Hayashi Kentaro <kenhys@gmail.com>
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
Holds the RFS template plugin.
"""

__author__ = 'Hayashi Kentaro'
__copyright__ = 'Copyright © 2016 Hayashi Kentaro'
__license__ = 'MIT'

import logging
import os

from debian import deb822, copyright
from debexpo.lib import constants
from debexpo.plugins import BasePlugin

log = logging.getLogger(__name__)


class RfsTemplatePlugin(BasePlugin):

    def _extract_copyright_info(self):
        info = {}
        copyright_path = os.path.join(self.tempdir,
                                      "extracted/debian/copyright")
        with open(copyright_path, 'r') as f:
            context = copyright.Copyright(f)
            header = context.header
            if header.upstream_contact:
                info['author'] = header.upstream_contact[0]

            lic = header.license
            if lic:
                info['license'] = lic.synopsis

            if not lic:
                default_license = context.find_files_paragraph('*')
                if default_license:
                    info['license'] = default_license.license.synopsis
        return info

    def _extract_control_info(self):
        info = {}
        control_path = os.path.join(self.tempdir, "extracted/debian/control")
        with open(control_path, 'r') as f:
            content = deb822.Deb822(f)
            if 'Homepage' in content:
                info['url'] = content['Homepage']
        return info

    def test_rfs_template(self):
        """
        Tests whether there are enough information for RFS template.

        This plugin collects:

        - Upstream Author (from debian/copyright)
        - URL (from debian/control)
        - License (from debian/copyright)
        - Changelog (from debian/changelog)

        """
        log.debug('Checking whether there are enough information for RFS '
                  'template')
        upstream_author = "[fill in name and email of upstream]"
        upstream_license = "[fill in]"
        upstream_url = "[fill in URL of upstream's web site]"
        package_changelog = "[your most recent changelog entry]"

        package_changelog = self.changes['Changes']

        copyright_info = self._extract_copyright_info()
        control_info = self._extract_control_info()

        if 'author' in copyright_info:
            upstream_author = copyright_info['author']
        if 'license' in copyright_info:
            upstream_license = copyright_info['license']

        if 'url' in control_info:
            upstream_url = control_info['url']

        data = {
            'upstream-author': upstream_author,
            'upstream-url': upstream_url,
            'upstream-license': upstream_license,
            'package-changelog': package_changelog,
        }

        outcome = "RFS template information"
        severity = constants.PLUGIN_SEVERITY_INFO
        self.passed(outcome, data, severity)


plugin = RfsTemplatePlugin

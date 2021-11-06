#   maintaineremail.py - maintaineremail plugin
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

import email.utils
import re

from debexpo.plugins.models import BasePlugin, PluginSeverity


class PluginMaintainerEmail(BasePlugin):
    @property
    def name(self):
        return 'maintainer-email'

    def run(self, changes, source):
        """
        Tests whether the maintainer email is the same as the uploader email.
        """
        if not changes.maintainer:
            self.failed('No maintainer address found')

        uploader_emails = []
        maintainer_emails = email.utils.getaddresses([changes.maintainer])
        maintainer_email = maintainer_emails[0][1]

        if changes.dsc.uploaders:
            for _, uploader_email in \
                    email.utils.getaddresses([changes.dsc.uploaders]):
                uploader_emails.append(uploader_email)

        severity = PluginSeverity.info
        if changes.uploader.email == maintainer_email:
            outcome = '"Maintainer" email is the same as the uploader'
        elif changes.uploader.email in uploader_emails:
            outcome = 'The uploader is in the package\'s "Uploaders" ' \
                      'field'
        else:
            outcome = 'The uploader is not in the package\'s ' \
                      '"Maintainer" or "Uploaders" fields'
            severity = PluginSeverity.warning

        team_upload = re.compile(r'\b[Tt]eam\b\s*\b[Uu]pload*\b')
        if team_upload.search(changes.changes) is not None:
            outcome += ' (Team upload)'
            severity = PluginSeverity.info

        qa_upload = re.compile(r'\b[Qq][Aa]\b\s*\b[Uu]pload*\b')
        if qa_upload.search(changes.changes) is not None:
            if maintainer_email == 'packages@qa.debian.org':
                outcome = 'Maintainer is Debian QA Team (QA Upload)'
                severity = PluginSeverity.info
            else:
                outcome = 'Maintainer is not Debian QA Team (QA Upload)'
                severity = PluginSeverity.error

        data = {
            'user_is_maintainer': (severity == PluginSeverity.info),
            'user_email': changes.uploader.email,
            'maintainer_email': maintainer_email,
            'uploader_emails': uploader_emails,
            }

        self.add_result('maintainer-email', outcome, data, severity)

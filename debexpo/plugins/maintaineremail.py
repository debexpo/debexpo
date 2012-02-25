# -*- coding: utf-8 -*-
#
#   maintaineremail.py — maintaineremail plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
Holds the maintaineremail plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = ', '.join([
        'Copyright © 2008 Jonny Lamb',
        'Copyright © 2012 Nicolas Dandrimont',
        ])
__license__ = 'MIT'

import email.utils
import logging
import re

from debian import deb822

from debexpo.lib import constants
from debexpo.plugins import BasePlugin

from debexpo.model import meta
from debexpo.model.users import User

log = logging.getLogger(__name__)

class MaintainerEmailPlugin(BasePlugin):

    def test_maintainer_email(self):
        """
        Tests whether the maintainer email is the same as the uploader email.
        """
        if self.user_id is not None:
            log.debug('Checking whether the maintainer email is the same as the uploader email')

            user = meta.session.query(User).get(self.user_id)

            if user is not None:
                maintainer_name, maintainer_email = email.utils.parseaddr(self.changes['Maintainer'])
                uploader_emails = []

                dsc = deb822.Dsc(file(self.changes.get_dsc()))

                if 'Uploaders' in dsc:
                    for uploader_name, uploader_email in email.utils.getaddresses([dsc['Uploaders']]):
                        uploader_emails.append(uploader_email)

                severity = constants.PLUGIN_SEVERITY_INFO
                if user.email == maintainer_email:
                    log.debug('"Maintainer" email is the same as the uploader')
                    outcome = '"Maintainer" email is the same as the uploader'
                elif user.email in uploader_emails:
                    log.debug('The uploader is in the package\'s "Uploaders" field')
                    outcome = 'The uploader is in the package\'s "Uploaders" field'
                else:
                    log.warning('%s != %s' % (user.email, maintainer_email))
                    outcome = 'The uploader is not in the package\'s "Maintainer" or "Uploaders" fields'
                    severity = constants.PLUGIN_SEVERITY_WARNING

                data = {
                    'user-is-maintainer': (severity == constants.PLUGIN_SEVERITY_INFO),
                    'user-email': user.email,
                    'maintainer-email': maintainer_email,
                    'uploader-emails': uploader_emails,
                    }

                self.failed(outcome, data, severity)
        else:
            log.warning('Could not get the uploader\'s user details from the database')

plugin = MaintainerEmailPlugin

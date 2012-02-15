# -*- coding: utf-8 -*-
#
#   changeslist.py — changeslist plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
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
Holds the changeslist plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging

from debexpo.lib.email import Email
from debexpo.plugins import BasePlugin

import pylons

log = logging.getLogger(__name__)

class ChangesListPlugin(BasePlugin):

    def test_send_mail(self):
        """
        Send mail to changes list.
        """
        log.debug('Sending mail to changes list')

        if not pylons.config.get('debexpo.changes_list', None):
            return

        if pylons.config['debexpo.changes_list'] == '':
            return

        email = Email('changes_list')
        to = pylons.config['debexpo.changes_list']
        email.send([to], changes=self.changes,
                changes_contents=self.changes_contents.decode('ascii', 'ignore'),
                dest=self.changes.get_pool_path())

plugin = ChangesListPlugin

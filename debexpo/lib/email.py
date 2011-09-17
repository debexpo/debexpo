# -*- coding: utf-8 -*-
#
#   email.py — Helper class for sending and receiving email
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2011 Arno Töll <debian@toell.net>
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
Holds helper class for sending and receiving email. The latter is achieved to fetch mails from an IMAP mailbox
"""

# You don't like that line?
# Come over it. Or, alternatively don't call your local modules like Python standard libraries
from __future__ import absolute_import

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner, Copyright © 2011 Arno Töll'
__license__ = 'MIT'

import logging
import os
import smtplib
from mako.template import Template
from mako.lookup import TemplateLookup

import pylons
import debexpo.lib.helpers as h
from gettext import gettext
import routes.util
import imaplib
import email.parser

log = logging.getLogger(__name__)

class FakeC(object):
    def __init__(self, **kw):
        for key in kw:
            setattr(self, key, kw[key])

class Email(object):
    def __init__(self, template):
        """
        Class constructor. Sets useful class and template attributes.

        ``template``
            Name of the template to use for the email.
        """
        self.template = template
        self.server = pylons.config['global_conf']['smtp_server']
        self.auth = None

        # Look whether auth is required.
        if 'smtp_username' in pylons.config['global_conf'] and 'smtp_password' in pylons.config['global_conf']:
            if pylons.config['global_conf']['smtp_username'] != '' and pylons.config['global_conf']['smtp_password'] != '':
                self.auth = {
                    'username' : pylons.config['global_conf']['smtp_username'],
                    'password' : pylons.config['global_conf']['smtp_password']
                }

    def send(self, recipients=None, **kwargs):
        """
        Sends the email.

        ``recipients``
            List of email addresses of recipients.
        """
        if recipients is None or recipients is []:
            return

        log.debug('Getting mail template: %s' % self.template)

        to = ', '.join(recipients)
        sender = '%s <%s>' % (pylons.config['debexpo.sitename'], pylons.config['debexpo.email'])

        c = FakeC(to=to, sender=sender, config=pylons.config, **kwargs)

        template_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates/email/%s.mako' % self.template)
        lookup = TemplateLookup(directories=[os.path.dirname(template_file)])
        template = Template(filename=template_file, lookup=lookup, module_directory=pylons.config['app_conf']['cache_dir'])
        # Temporarily set up routes.util.url_for as the URL renderer used for h.url() in templates
        pylons.url._push_object(routes.util.url_for)
        message = template.render(_=gettext, h=h, c=c)
        pylons.url._pop_object()

        log.debug('Starting SMTP session to %s' % self.server)
        session = smtplib.SMTP(self.server)

        if self.auth:
            log.debug('Authentication requested; logging in')
            session.login(self.auth['user'], self.auth['password'])

        log.debug('Sending email to %s' % ', '.join(recipients))
        result = session.sendmail(pylons.config['debexpo.email'], recipients, message)

        if result:
            # Something went wrong.
            for recipient in result.keys():
                log.critical('Failed sending to %s: %s, %s' % (recipient, result[recipient][0],
                    result[recipient][1]))
        else:
            log.debug('Successfully sent')


    def _check_error(self, msg, err, data = None):
        if err != 'OK':
            if (data):
                self.log.error("%s failed: %s" % (msg, data))
            else:
                self.log.error("%s failed: %s" % (msg))

    def unread_messages(self, filter_pattern):
        if not self.connection_established():
            return

        (err, messages) = self.imap.search(None, '(UNSEEN)')
        self._check_error("IMAP search messages", err)

        for msg_id in messages[0].split(" "):
            #(err, msginfo) = self.imap.fetch(msg_id, '(BODY[HEADER.FIELDS (SUBJECT FROM LIST-ID)])')
            (err, msginfo) = self.imap.fetch(msg_id, 'RFC822')
            self._check_error("IMAP fetch message", err)
            if (err != 'OK'):
                continue
            ep = email.parser.Parser().parsestr(msginfo[0][1])
            if not filter_pattern[0] in ep:
                log.debug("No such header in message: %s" % (filter_pattern[0]))
                continue
            if ep[filter_pattern[0]] in filter_pattern[1]:
                yield ep
            else:
                self.log.debug("Unrecognized message in mailbox: '%s'" % ep["subject"])


    def connect_to_server(self):
        self.established = False
        self.imap = imaplib.IMAP4(pylons.config['debexpo.imap_server'])
        (err, data) = self.imap.login(pylons.config['debexpo.imap_user'], pylons.config['debexpo.imap_password'])
        self._check_error("IMAP login", err, data)
        if err == 'OK':
            self.established = True

        (err, data) = self.imap.select("INBOX", readonly=True)
        self._check_error("IMAP select", err, data)

    def disconnect_from_server(self):
        self.imap.close()
        self.imap.logout()


    def connection_established(self):
        if not self.established:
            log.debug("Connection to IMAP server not established");
            return False
        return True

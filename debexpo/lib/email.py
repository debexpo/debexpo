# -*- coding: utf-8 -*-
#
#   email.py — Helper class for sending and receiving email
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
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

import email
import email.charset
import email.errors
import email.header
import email.mime.text

import logging
import os
import smtplib
from mako.template import Template
from mako.lookup import TemplateLookup

import pylons
import debexpo.lib.helpers as h
from gettext import gettext
import routes.util
import nntplib
import email.parser

log = logging.getLogger(__name__)

class FakeC(object):
    def __init__(self, **kw):
        for key in kw:
            value = kw[key]
            if isinstance(value, str):
                value = value.decode("utf-8")
            setattr(self, key, value)

class Email(object):
    def __init__(self, template):
        """
        Class constructor. Sets useful class and template attributes.

        ``template``
            Name of the template to use for the email.
        """
        self.template = template
        self.server = pylons.config['global_conf']['smtp_server']
        if 'smtp_port' in pylons.config['global_conf']:
            self.port = pylons.config['global_conf']['smtp_port']
        else:
            self.port = smtplib.SMTP_PORT
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

        rendered_message = template.render_unicode(_=gettext, h=h, c=c).encode("utf-8")

        try:
            # Parse the email message
            message = email.message_from_string(rendered_message)
        except email.errors.MessageParseError:
            # Parsing the message failed, let's send the raw data...
            message = rendered_message.encode("utf-8")
        else:
            # By default, python base64-encodes all UTF-8 text which is annoying. Force quoted-printable
            email.charset.add_charset('utf-8', email.charset.QP, email.charset.QP, 'utf-8')
            # Create a new, MIME-aware message
            new_message = email.mime.text.MIMEText(message.get_payload().decode("utf-8"), "plain", "utf-8")

            for key in message.keys():
                try:
                    contents = message[key].decode("utf-8").split(u" ")
                except UnicodeDecodeError:
                    # Bad encoding in the header, don't try to do anything more...
                    header = message[key]
                else:
                    # Do some RFC2047-encoding of the headers.  We split on word-boundaries so that
                    # python doesn't encode the whole header in a RFC2047 blob, but only what's
                    # needed.
                    header = email.header.Header()
                    for c in contents:
                        header.append(c)
                new_message[key] = header
            # And get that back as a string to pass onto sendmail
            message = new_message.as_string()

        pylons.url._pop_object()

        log.debug('Starting SMTP session to %s:%s' % (self.server, self.port))
        session = smtplib.SMTP(self.server, self.port)

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
                log.error("%s failed: %s" % (msg, data))
            else:
                log.error("failed: %s" % (msg))

    def unread_messages(self, list_name, changed_since):
        if not self.connection_established():
            return

        try:
            (_, count, first, last, _) = self.nntp.group(list_name)
            log.debug("Fetching messages %s to %s on %s" % (changed_since, last, list_name))
        except nntplib.NNTPError as e:
            self.established = False
            log.error("Connecting to NNTP server %s failed: %s" % (pylons.config['debexpo.nntp_server'], str(e)))
            return
        except EOFError:
            self.established = False
            log.error("NNTP server %s closed connection" % (pylons.config['debexpo.nntp_server']))
            return

        try:
            (_, messages) = self.nntp.xover(str(changed_since), str(last))

            for (msg_num, _, _, _, msg_id, _, _, _) in messages:
                (_, _, _, response) = self.nntp.article(msg_id)
                ep = email.parser.Parser().parsestr(reduce(lambda x,xs: x+"\n"+xs, response))
                ep['X-Debexpo-Message-ID'] = msg_id;
                ep['X-Debexpo-Message-Number'] = msg_num;
                yield ep
        except nntplib.NNTPError as e:
            log.error("Connecting to NNTP server %s failed: %s" % (pylons.config['debexpo.nntp_server'], str(e)))
            return

    def connect_to_server(self):
        self.established = False
        try:
            self.nntp = nntplib.NNTP(pylons.config['debexpo.nntp_server'])
        except nntplib.NNTPError as e:
            log.error("Connecting to NNTP server %s failed: %s" % (pylons.config['debexpo.nntp_server'], str(e)))
            return

        self.established = True

    def disconnect_from_server(self):
        self.nntp.quit()
        self.established = False

    def connection_established(self):
        if not self.established:
            self.connect_to_server()
            if not self.established:
                log.debug("Connection to NNTP server not established");
            return self.established
        return True


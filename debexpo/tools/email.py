#   email.py — Helper class for sending mail
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2011 Arno Töll <debian@toell.net>
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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
Holds helper class for sending email.
"""

import email
import email.charset
import email.errors
import email.header
import email.mime.text
import email.parser
import logging
import smtplib

from django.conf import settings
from django.template.loader import render_to_string

log = logging.getLogger(__name__)


class Email(object):
    def __init__(self, template):
        """
        Class constructor. Sets useful class and template attributes.

        ``template``
            Name of the template to use for the email.
        """
        self.template = template
        self.server = settings.SMTP_SERVER
        self.port = settings.SMTP_PORT
        self.mbox = settings.TEST_SMTP
        self.bounce = settings.BOUNCE_EMAIL
        self.auth = None

        # Look whether auth is required.
        if (all(hasattr(settings, attr) for attr in ('SMTP_USERNAME',
                                                     'SMTP_PASSWORD'))):
            self.auth = {
                'username': settings.SMTP_USERNAME,
                'password': settings.SMTP_PASSWORD
            }

    def send(self, recipients=None, **kwargs):
        """
        Sends the email.

        ``recipients``
            List of email addresses of recipients.
        """
        if not recipients:
            return

        content = self._render_content(recipients, **kwargs)
        mail = self._render_mail(content)

        if self.mbox:
            return self._save_as_file(recipients, mail)

        return self._send_as_mail(recipients, mail)  # pragma: no cover

    def _render_content(self, recipients, **kwargs):
        log.debug('Getting mail template: %s' % self.template)

        to = ', '.join(recipients)
        sender = '{} <{}>'.format(settings.SITE_NAME,
                                  settings.SUPPORT_EMAIL)

        return render_to_string(self.template, {
            'settings': settings,
            'to': to,
            'sender': sender,
            'args': kwargs
        })

    def _render_mail(self, content):
        try:
            # Parse the email message
            message = email.message_from_string(content)
        except email.errors.MessageParseError:  # pragma: no cover
            # Parsing the message failed, let's send the raw data...
            message = content.encode("utf-8")
        else:
            # By default, python base64-encodes all UTF-8 text which is
            # annoying. Force quoted-printable
            email.charset.add_charset('utf-8', email.charset.QP,
                                      email.charset.QP, 'utf-8')
            # Create a new, MIME-aware message
            new_message = email.mime.text.MIMEText(
                message.get_payload(), "plain", "utf-8")

            for key in message.keys():
                try:
                    contents = message[key].split(" ")
                except UnicodeDecodeError:  # pragma: no cover
                    # Bad encoding in the header, don't try to do anything
                    # more...
                    header = message[key]
                else:
                    # Do some RFC2047-encoding of the headers.  We split on
                    # word-boundaries so that python doesn't encode the whole
                    # header in a RFC2047 blob, but only what's needed.
                    header = email.header.Header()
                    for c in contents:
                        header.append(c)
                new_message[key] = header
            # And get that back as a string to pass onto sendmail
            message = new_message.as_string()

        return message

    def _save_as_file(self, recipients, message):
        log.debug('Save email as file to {}'.format(self.server))

        try:
            with open(self.mbox, 'a') as email:
                email.write(message)
        except OSError as e:
            log.error('Could not write mbox: {}'.format(e))

            return False

        return True

    # This would require a live SMTP to test.
    def _send_as_mail(self, recipients, message):  # pragma: no cover
        # Connect
        log.debug('Starting SMTP session to {}: {}'.format(self.server,
                                                           self.port))
        try:
            session = smtplib.SMTP(self.server, self.port)
        except smtplib.SMTPException as e:
            log.error('Could not connect to SMTP: {}'.format(e))

            return False

        # Authenticate
        if self.auth:
            log.debug('Authentication requested, logging in')
            try:
                session.login(self.auth['user'], self.auth['password'])
            except smtplib.SMTPException as e:
                log.error('Could not authenticate: {}'.format(e))
                session.quit()

                return False

        # Send
        log.debug('Sending email to {}'.format(', '.join(recipients)))
        try:
            result = session.sendmail(self.bounce,
                                      recipients, message)
        except smtplib.SMTPException as e:
            log.error('Could not send mail: {}'.format(e))
            session.quit()

            return False

        # Quit
        session.quit()

        if result:
            # Something went wrong.
            for recipient in result.keys():
                log.critical('Failed sending to {}: {}, {}'.format(
                             (recipient, result[recipient][0],
                              result[recipient][1])))

                return False

        log.debug('Successfully sent')

        return True

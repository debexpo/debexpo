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

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

log = logging.getLogger(__name__)


class Email():
    def __init__(self, template):
        """
        Class constructor. Sets useful class and template attributes.

        ``template``
            Name of the template to use for the email.
        """
        self.template = template

    def send(self, subject, recipients=None,
             from_email=None,
             reply_to=None,
             bounce_to=None,
             headers={}, **kwargs):
        """
        Sends the email.

        ``recipients``
            List of email addresses of recipients.
        """
        if not recipients:
            return

        if not from_email:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')

        if not bounce_to:
            bounce_to = getattr(settings, 'DEFAULT_BOUNCE_EMAIL')

        headers['From'] = from_email

        body = self._render_content(recipients, **kwargs)
        self.email = EmailMessage(
            subject,
            body,
            from_email=bounce_to,
            to=recipients,
            reply_to=reply_to,
            headers=headers
        )
        self.email.send()

    def _render_content(self, recipients, **kwargs):
        log.debug('Getting mail template: %s' % self.template)

        to = ', '.join(recipients)

        return render_to_string(self.template, {
            'settings': settings,
            'to': to,
            'args': kwargs
        })

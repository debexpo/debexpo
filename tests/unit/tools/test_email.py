#   test_mail.py - Test mail class
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
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

from os import unlink
from os.path import isfile

from django.test import TestCase
from django.conf import settings

from debexpo.tools.email import Email


class TestMail(TestCase):
    def setUp(self):
        self.email = Email('email-test.eml')

    def tearDown(self):
        if isfile(settings.TEST_SMTP):
            unlink(settings.TEST_SMTP)

    def test_render_content(self):
        content = self.email._render_content(['user@example.org'])
        self._assert_base_content(content)

    def test_message_content(self):
        content = self.email._render_content(['user@example.org'])
        mail = self.email._render_mail(content)
        self._assert_mail_content(mail)

    def test_kwargs(self):
        email = Email('email-test-kwargs.eml')
        email.send(['user@example.org'], content='value')

        with open(settings.TEST_SMTP, 'r') as mbox:
            content = mbox.read()
            self._assert_mail_content(content)
            self.assertIn('value', content)

    def test_mbox(self):
        self.email.send(['user@example.org'])

        with open(settings.TEST_SMTP, 'r') as mbox:
            self._assert_mail_content(mbox.read())

    def test_fail_mailbox(self):
        mbox = settings.TEST_SMTP
        settings.TEST_SMTP = '/proc/sys'

        email = Email('email-test.eml')
        self.assertFalse(email.send(['user@example.org']))

        settings.TEST_SMTP = mbox

    def test_no_recipients(self):
        self.email.send()
        self.assertFalse(isfile(settings.TEST_SMTP))

        self.email.send([])
        self.assertFalse(isfile(settings.TEST_SMTP))

    def test_auth_parameters(self):
        settings.SMTP_USERNAME = 'foo'
        settings.SMTP_PASSWORD = 'CHANGEME'

        email = Email('email-test.eml')
        self.assertEquals(email.auth, {'username': 'foo',
                                       'password': 'CHANGEME'})

    def _assert_mail_content(self, content):
        self._assert_base_content(content)
        self.assertIn('Content-Type: text/plain; charset="utf-8"', content)

    def _assert_base_content(self, content):
        self.assertIn('This is a test email, user@example.org', content)
        self.assertIn('From: debexpo <support@example.org>', content)
        self.assertIn('To: user@example.org', content)

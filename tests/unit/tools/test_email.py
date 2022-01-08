#   test_mail.py - Test mail class
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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

from django.core import mail
from django.test import TestCase
from debexpo.tools.email import Email


class TestMail(TestCase):
    def setUp(self):
        self.email = Email('email-test.eml')

    def test_render_content(self):
        content = self.email._render_content(['user@example.org'])
        self._assert_base_content(content)

    def test_kwargs(self):
        email = Email('email-test-kwargs.eml')
        email.send('My subject', ['user@example.org'], content='value')

        self._assert_mail_content(mail.outbox[0])
        self.assertIn('value', mail.outbox[0].body)

    def test_no_recipients(self):
        self.email.send('My subject')
        self.assertFalse(hasattr(self.email, 'email'))

        self.email.send('My subject', [])
        self.assertFalse(hasattr(self.email, 'email'))

    def _assert_mail_content(self, content, bounce='bounce@example.org'):
        self._assert_base_content(content.body)
        self.assertIn('user@example.org', content.to)
        self.assertIn(bounce, content.from_email)
        self.assertIn('From: debexpo <support@example.org>',
                      str(content.message()))

    def _assert_base_content(self, content):
        self.assertIn('This is a test email, user@example.org', content)

    def test_bounce(self):
        bounce = 'another@example.org'
        self.email.send('My subject', ['user@example.org'],
                        bounce_to=bounce)

        self._assert_mail_content(mail.outbox[0], bounce=bounce)

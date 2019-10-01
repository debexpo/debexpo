#   test_nntp.py - Test nntp client
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

import unittest
from email.message import Message

from django.conf import settings
from django.test import TestCase, tag

from debexpo.tools.nntp import NNTPClient
from tests.tools import test_network


@tag('network', 'nntp')
@unittest.skipIf(test_network(), 'no network: {}'.format(test_network()))
class TestNNTP(TestCase):
    def setUp(self):
        self.client = NNTPClient()
        self.list = 'gmane.linux.debian.devel.changes.stable'
        self.payload = 'kernel-build-2.4.22-2_2.4.22-2woody.2_alpha.deb'

    def test_nntp_no_connection(self):
        self.assertFalse(self.client.connected)
        self.assertRaises(StopIteration, next,
                          self.client.unread_messages('list', 1))

    def test_nntp_disconnect_no_connection(self):
        self.assertFalse(self.client.disconnect_from_server())
        self.test_nntp_no_connection()

        # Simulate already disconnected server
        self.client.connected = True
        self.assertTrue(self.client.disconnect_from_server())
        self.test_nntp_no_connection()

    def test_connect_wrong_server(self):
        server = settings.NNTP_SERVER
        settings.NNTP_SERVER = 'thistlddoesnotexists'

        client = NNTPClient()
        self.assertFalse(client.connect_to_server())

        settings.NNTP_SERVER = server

    def test_nntp(self):
        # Connect to NNTP server
        self.assertTrue(self.client.connect_to_server())
        self.assertTrue(self.client.connected)

        # Can't connect twice
        self.assertFalse(self.client.connect_to_server())
        self.assertTrue(self.client.connected)

        # Get message from list
        message = next(self.client.unread_messages(self.list, '1'))
        self.assertTrue(message)
        self.assertIsInstance(message, Message)
        self.assertIn(self.payload, message.get_payload(decode=True).decode())

        # Disconnect
        self.assertTrue(self.client.disconnect_from_server())
        self.assertFalse(self.client.connected)

    def test_nntp_wrong_list(self):
        self.assertTrue(self.client.connect_to_server())
        self.assertRaises(StopIteration, next,
                          self.client.unread_messages('list', 1))
        self.assertTrue(self.client.disconnect_from_server())

    def test_nntp_wrong_index(self):
        self.assertTrue(self.client.connect_to_server())
        self.assertRaises(StopIteration, next,
                          self.client.unread_messages(self.list, '-1'))
        self.assertTrue(self.client.disconnect_from_server())

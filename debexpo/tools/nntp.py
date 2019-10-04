#   nntp.py — NNTP client
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
Holds helper class for receiving from NNTP server.
"""

import email
import email.charset
import email.errors
import email.header
import email.mime.text
import email.parser
import logging
import nntplib

from django.conf import settings

log = logging.getLogger(__name__)


class NNTPClient(object):
    def __init__(self):
        self.connected = False
        self.server = settings.NNTP_SERVER

    def unread_messages(self, list_name, changed_since):
        if not self.connected:
            log.warn('Tried to read messages while not connected to NNTP '
                     'server')
            return

        try:
            (_, count, first, last, _) = self.nntp.group(list_name)
            log.debug("Fetching messages {} to {} on {}".format(changed_since,
                                                                last,
                                                                list_name))
        except Exception as e:
            log.error("Failed to communicate with NNTP server {}: {}".format(
                      self.server, e))
            return

        try:
            (_, messages) = self.nntp.xover(str(changed_since), str(last))

            for (msg_num, overview) in messages:
                (_, response) = self.nntp.article(overview['message-id'])
                ep = email.parser.BytesParser() \
                    .parsebytes(b"\n".join(response.lines))
                ep['X-Debexpo-Message-ID'] = overview['message-id']
                ep['X-Debexpo-Message-Number'] = msg_num
                yield ep
        except Exception as e:
            log.error("Failed to communicate with NNTP server {}: {}".format(
                      self.server, e))
            return

    def connect_to_server(self):
        if self.connected:
            log.debug('Already connected to NNTP server')
            return False

        try:
            self.nntp = nntplib.NNTP(self.server)
        except Exception as e:
            log.error("Connecting to NNTP server {} failed: {}".format(
                      self.server, e))
            return False

        self.connected = True
        return True

    def disconnect_from_server(self):
        if not self.connected:
            log.debug('Not connected to NNTP server')
            return False

        try:
            self.nntp.quit()
        except Exception as e:
            log.error("Disconnecting to NNTP server {} failed: {}".format(
                      self.server, e))

        self.connected = False
        return True

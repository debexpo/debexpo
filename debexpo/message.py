# -*- coding: utf-8 -*-
#
#   message.py — Setup the fedmsg context for use within Debexpo
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2013 Simon Chopin <chopin.simon@gmail.com>
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
Setup a fedmsg context suitable for Debexpo.
"""

__author__ = 'Simon Chopin'
__copyright__ = 'Copyright © 2013 Simon Chopin'
__license__ = 'MIT'

from fedmsg.core import FedMsgContext
from fedmsg.config import load_config
from threading import Lock

config = load_config([], None)

config['name'] = "relay_inbound"
config['active'] = True
# XXX: Should be taken from the debexpo config!

__context = FedMsgContext(**config)
__context_lock = Lock()

def publish(**kw):
    __context_lock.acquire()
    __context.publish(**kw)
    __context_lock.release()

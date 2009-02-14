# -*- coding: utf-8 -*-
#
#   debian.py — Debian controller for accessing the repository
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
This module holds the Debian controller which manages the /debian/ directory.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import os
import logging
import paste.fileapp

from debexpo.lib.base import *

log = logging.getLogger(__name__)

class DebianController(BaseController):
    """
    Class for handling the /debian/ directory.
    """

    def index(self, filename):
        """
        Entry point to the controller. Opens a file in the repository using Paste's
        FileApp.
        """
        file = os.path.join(config['debexpo.repository'], filename)
        log.debug('%s requested' % filename)

        content_type = None
        if filename.endswith('.dsc'):
            content_type = 'text/plain'

        if os.path.isfile(file):
            fapp = paste.fileapp.FileApp(file, content_type=content_type)
        else:
            log.error('File not found')
            abort(404, 'File not found')

        return fapp(request.environ, self.start_response)

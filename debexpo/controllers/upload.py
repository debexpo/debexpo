# -*- coding: utf-8 -*-
#
#   upload.py — Upload controller
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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
Holds the UploadController class.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import os
import os.path
import logging
import base64

try:
    from sqlalchemy.exceptions import InvalidRequestError
except ImportError: # for sqlalchemy 0.7.1 and above
    from sqlalchemy.exc import InvalidRequestError

from debexpo.lib.base import *
from debexpo.lib.filesystem import CheckFiles
from debexpo.model import meta

log = logging.getLogger(__name__)

class UploadController(BaseController):
    """
    Controller to handle uploading packages via HTTP PUT.
    """

    def index(self, filename):
        """
        Controller entry point. When dput uploads a package via `PUT`, the connection below is made::

          PUT /upload/packagename_version.dsc

        assuming the file being uploaded is the `dsc`.

        This method takes writes the uploaded file to disk and calls the import script in another
        process.

        ``filename``
            Name of file being uploaded.

        The password here is actually a user_upload_key, not the user password.
        """
        if request.method != 'PUT':
            log.error('Request with method %s attempted on Upload controller.' % request.method)
            abort(405, 'The upload controller only deals with PUT requests.', headers=[('Allow', 'PUT')])

        log.debug('File upload: %s' % filename)


        # Check whether the file extension is supported by debexpo
        if not CheckFiles().allowed_upload(filename):
            log.error('File type not supported: %s' % filename)
            abort(403, 'The uploaded file type is not supported')

        if 'debexpo.upload.incoming' not in config:
            log.critical('debexpo.upload.incoming variable not set')
            abort(500, 'The incoming directory has not been set')

        if not os.path.isdir(config['debexpo.upload.incoming']):
            log.critical('debexpo.upload.incoming is not a directory')
            abort(500, 'The incoming directory has not been set up')

        if not os.access(config['debexpo.upload.incoming'], os.W_OK):
            log.critical('debexpo.upload.incoming is not writable')
            abort(500, 'The incoming directory has not been set up')

        save_path = os.path.join(os.path.join(config['debexpo.upload.incoming'], "pub"), filename)
        log.debug('Saving uploaded file to: %s', save_path)
        if os.path.exists(save_path):
                log.debug("Aborting. File already exists")
                abort(403, 'The file was already uploaded')
        f = open(save_path, 'wb')

        # The body attribute now contains the entire contents of the uploaded file.
        # TODO: This looks dangerous if huge files are loaded into memory.
        f.write(request.body)
        f.close()



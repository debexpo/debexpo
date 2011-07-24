# -*- coding: utf-8 -*-
#
#   upload.py — Upload controller
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
import logging
import subprocess
import md5
import base64

try:
    from sqlalchemy.exceptions import InvalidRequestError
except ImportError: # for sqlalchemy 0.7.1 and above
    from sqlalchemy.exc import InvalidRequestError

from debexpo.lib.base import *
from debexpo.lib.utils import allowed_upload
from debexpo.model import meta
from debexpo.model.user_upload_key import UserUploadKey

log = logging.getLogger(__name__)

class UploadController(BaseController):
    """
    Controller to handle uploading packages via HTTP PUT.
    """

    def index(self, filename, email, password):
        """
        Controller entry point. When dput uploads a package via `PUT`, the connection below is made::

          PUT /upload/packagename_version.dsc

        assuming the file being uploaded is the `dsc`.

        This method takes writes the uploaded file to disk and calls the import script in another
        process.

        ``filename``
            Name of file being uploaded.

        ``email`` (optional)
            Used when requesting the URL /upload/email/password/filename scheme.

        ``password`` (optional)
            Used when requesting the URL /upload/email/password/filename scheme.

        The password here is actually a user_upload_key, not the user password.
        """
        if request.method != 'PUT':
            log.error('Request with method %s attempted on Upload controller.' % request.method)
            abort(405, 'The upload controller only deals with PUT requests.', headers=[('Allow', 'PUT')])

        log.debug('File upload: %s' % filename)

        # Check the uploader's username and password
        try:
            # Get user from database
            import logging
            logging.error(email)
            logging.error(password)
            user_upload_key = meta.session.query(UserUploadKey).filter_by(
                upload_key=password).one()
            if user_upload_key.user.email == email:
                user = user_upload_key.user
            log.debug('Authenticated as %s <%s>' % (user.name, user.email))
        except InvalidRequestError, e:
            # Couldn't get one() row, therefore unsuccessful authentication
            abort(403, 'Authentication failed.')


        # Check whether the file extension is supported by debexpo
        if not allowed_upload(filename):
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

        save_path = os.path.join(config['debexpo.upload.incoming'], filename)
        log.debug('Saving uploaded file to: %s', save_path)
        f = open(save_path, 'wb')

        # The body attribute now contains the entire contents of the uploaded file.
        # TODO: This looks dangerous if huge files are loaded into memory.
        f.write(request.body)
        f.close()

        # The .changes file is always sent last, so after it is sent,
        # call the importer process.
        if filename.endswith('.changes'):
            command = '%s -i %s -c %s -u %s' % (config['debexpo.importer'],
                config['global_conf']['__file__'], filename, user.id)

            subprocess.Popen(command, shell=True, close_fds=True)


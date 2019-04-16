# -*- coding: utf-8 -*-
#
#   upload.py — Upload controller
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
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

from glob import glob

from debexpo.lib.base import BaseController, abort, config, request
from debexpo.lib.filesystem import CheckFiles
from debexpo.lib.changes import Changes

log = logging.getLogger(__name__)


class UploadController(BaseController):
    """
    Controller to handle uploading packages via HTTP PUT.
    """

    def _queued_for_import(self, filename):
        # File does not exist. Return now
        if not os.path.exists(filename):
            return False

        log.debug("File already exists: {}".format(filename))

        # Changes file can't be overwritten
        if filename.endswith('.changes'):
            log.debug("Changes file can't be overwritten. Abort upload.")
            return True

        # For each changes files...
        for changes_file in glob(os.path.join(self.incoming_dir, '*.changes')):
            try:
                changes = Changes(filename=changes_file)
            except Exception as e:
                log.debug("Failed to parse changes file {}: "
                          "{}".format(changes_file, e))
                continue

            # ... check that filename is not referenced
            for referenced_file in changes.get_files():
                if referenced_file == os.path.basename(filename):
                    log.debug("File queued for importation. Abort upload.")
                    return True

        # Look like an interrupted upload. Allow to reupload
        log.debug("File not referenced by any changes. "
                  "Allowing overwrite.")
        return False

    def index(self, filename):
        """
        Controller entry point. When dput uploads a package via `PUT`, the
        connection below is made::

          PUT /upload/packagename_version.dsc

        assuming the file being uploaded is the `dsc`.

        This method takes writes the uploaded file to disk and calls the import
        script in another process.

        ``filename``
            Name of file being uploaded.

        The password here is actually a user_upload_key, not the user password.
        """
        if request.method != 'PUT':
            log.error('Request with method %s attempted on Upload controller.' %
                      request.method)
            abort(405, 'The upload controller only deals with PUT requests.',
                  headers=[('Allow', 'PUT')])

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

        self.incoming_dir = os.path.join(config['debexpo.upload.incoming'],
                                         'pub')
        if not os.path.isdir(self.incoming_dir):
            os.mkdir(self.incoming_dir)
        save_path = os.path.join(self.incoming_dir, filename)
        log.debug('Saving uploaded file to: %s', save_path)
        if self._queued_for_import(save_path):
            abort(403, 'The file was already uploaded')
        f = open(save_path, 'wb')

        # The body attribute now contains the entire contents of the uploaded
        # file.
        # TODO: This looks dangerous if huge files are loaded into memory.
        f.write(request.body)
        f.close()

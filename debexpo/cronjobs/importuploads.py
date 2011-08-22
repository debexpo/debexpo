# -*- coding: utf-8 -*-
#
#   importuploads.py — Import FTP uploads to Debexpo
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2011 Arno Töll <debian@toell.net>
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
Import FTP uploads to Debexpo
"""
__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2011 Arno Töll'
__license__ = 'MIT'

from debexpo.cronjobs import BaseCronjob

import glob
import os
import subprocess

class ImportUpload(BaseCronjob):
    def setup(self):
        """
        This method does nothing in this cronjob
        """
        pass

    def teardown(self):
        """
        This method does nothing in this cronjob
        """
        pass

    def deploy(self):
        """
        Loops through the debexpo.upload.incoming directory and runs the debexpo.importer for each file
        """
        if 'debexpo.upload.incoming' not in self.config or not os.path.isdir(self.config['debexpo.upload.incoming']):
            self.log.critical("debexpo.upload.incoming was not configured")
            return

        for file in glob.glob( os.path.join(self.config['debexpo.upload.incoming'], '*.changes') ):
            self.log.debug("Import upload: %s\n" % (file))
            command = [ self.config['debexpo.importer'], '-i', self.config['global_conf']['__file__'], '-c', file ]
            subprocess.Popen(command, close_fds=True)
        else:
            self.log.debug("No files in the queue")

cronjob = ImportUpload
schedule = 5

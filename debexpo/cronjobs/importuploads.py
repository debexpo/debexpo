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
import os.path
import subprocess
import datetime
import shutil

import debexpo.lib.filesystem
from debexpo.lib.changes import Changes

class NotCompleteUpload(Exception): pass

class ImportUpload(BaseCronjob):
    def setup(self):
        """
        This method does nothing in this cronjob
        """
        self.stale_files = []
        self.files = debexpo.lib.filesystem.CheckFiles()
        self.log.debug("%s loaded successfully" % (__name__))

    def teardown(self):
        """
        This method does nothing in this cronjob
        """
        pass

    def invoke(self):
        """
        Loops through the debexpo.upload.incoming directory and runs the debexpo.importer for each file
        """
        if 'debexpo.upload.incoming' not in self.config or not os.path.isdir(self.config['debexpo.upload.incoming']):
            self.log.critical("debexpo.upload.incoming was not configured")
            return

        # 1) Process uploads
        for file in glob.glob( os.path.join(os.path.join(self.config['debexpo.upload.incoming'], "pub"), '*.changes') ):
            try:
                changes = Changes(filename=file)
            except:
                self.log.error('Invalid changes file: %s' % (file))
                continue

            try:
                for filename in changes.get_files() + [ changes.get_filename(), ]:
                    source_file = os.path.join(os.path.join(self.config['debexpo.upload.incoming'], "pub"), filename)
                    destination_file = os.path.join(self.config['debexpo.upload.incoming'], filename)

                    if not os.path.exists(source_file):
                            self.log.debug("Source file %s does not exist - putting upload on hold" % (source_file))
                            raise NotCompleteUpload;
                    if os.path.exists(destination_file):
                            self.log.debug("Do not import %s: already exists on destination path - removing file instead" % (source_file))
                            os.remove(source_file)
                            raise NotCompleteUpload;
                    shutil.move(source_file, self.config['debexpo.upload.incoming'])
            except NotCompleteUpload:
                continue

            self.log.info("Import upload: %s" % (file))
            command = [ self.config['debexpo.importer'], '-i', self.config['global_conf']['__file__'], '-c', changes.get_filename() ]
            self.log.debug("Executing: %s" % (" ".join(command)))
            proc = subprocess.Popen(command, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (istdout, istderr) = proc.communicate()
            if proc.returncode != 0:
                self.log.critical("Importer failed to import package %s [err=%d]." % (file, proc.returncode))
                self.log.debug("Output was\n%s\n%s" % (istdout,istderr))

        # 2) Mark unprocessed files and get rid of them after some time
        pub = os.path.join(self.config['debexpo.upload.incoming'], "pub")
        filenames = [name for (name, _) in self.stale_files]
        file_to_check = []
        for file in glob.glob( os.path.join(pub, '*') ):
            if self.files.allowed_upload(file):
                self.log.debug("Incomplete upload: %s" % (file))
                if not file in filenames:
                    self.stale_files.append((file,datetime.datetime.now()))
                else:
                    file_to_check.append(file)
            else:
                if os.path.isfile(file):
                    self.log.warning("Remove unknown file: %s" % (file))
                    os.remove(file)

        for file in file_to_check:
            for (file_known, last_check) in self.stale_files:
                if file == file_known and (datetime.datetime.now() - last_check) > datetime.timedelta(hours = 6):
                    if os.path.isfile(file):
                        self.log.warning("Remove incomplete upload: %s" % (file))
                        os.remove(file)


cronjob = ImportUpload
schedule = datetime.timedelta(minutes = 10)

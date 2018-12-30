# -*- coding: utf-8 -*-
#
#   importuploads.py — Import FTP uploads to Debexpo
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
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
import itertools
import os
import os.path
import time
import datetime
import shutil

import debexpo.lib.filesystem
from debexpo.lib.changes import Changes
from debexpo.importer.importer import Importer

class NotCompleteUpload(Exception): pass

class ImportUpload(BaseCronjob):
    def setup(self):
        """
        This method does nothing in this cronjob
        """
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
        base_path = os.path.join(self.config['debexpo.upload.incoming'], "pub")
        directories = [base_path, os.path.join(base_path, 'pub/UploadQueue')]
        for changes_file in sum((glob.glob(os.path.join(directory, '*.changes')) for directory in directories), []):
            try:
                parsed_changes = Changes(filename=changes_file)
            except:
                self.log.exception('Invalid changes file: %s' % changes_file)
                continue

            try:
                directory = os.path.dirname(changes_file)
                uploaded_files = parsed_changes.get_files() + [parsed_changes.get_filename()]
                for filename in uploaded_files:
                    source_file = os.path.join(directory, filename)
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


            self.log.info("Import upload: %s" % (changes_file))
	    importer = Importer(parsed_changes.get_filename(),
				self.config['global_conf']['__file__'],
				False,
				False)

	    returncode = importer.main(no_env=True)
            if returncode != 0:
                self.log.critical("Importer failed to import package %s [err=%d]." % (changes_file, returncode))
            for filename in uploaded_files:
                destination_file = os.path.join(self.config['debexpo.upload.incoming'], filename)
                if os.path.exists(destination_file):
                    self.log.debug("Remove stale file %s - the importer probably crashed" % (destination_file))
                    os.remove(destination_file)

        # 2) Mark unprocessed files and get rid of them after some time
        pub = os.path.join(self.config['debexpo.upload.incoming'], "pub")
        for file in glob.glob( os.path.join(pub, '*') ):
            if self.files.allowed_upload(file):
                self.log.debug("Incomplete upload: %s" % (file))
                last_change = time.time() - os.stat(file).st_mtime
                # the file was uploaded more than 6 hours ago
                if last_change > 6 * 60 * 60:
                    self.log.warning("Remove old file: %s (last modified %.2f hours ago)" % (file, last_change / 3600.))
                    os.remove(file)
            else:
                if os.path.isfile(file):
                    self.log.warning("Remove unknown file: %s" % (file))
                    os.remove(file)

cronjob = ImportUpload
schedule = datetime.timedelta(minutes = 10)

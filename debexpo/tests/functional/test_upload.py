# -*- coding: utf-8 -*-
#
#   test_upload.py — UploadController test cases
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2012 Nicolas Dandrimont <nicolas.dandrimont@crans.org>
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
UploadController test cases.
"""

__author__ = 'Jonny Lamb'
__copyright__ = ', '.join([
        'Copyright © 2008 Jonny Lamb',
        'Copyright © 2010 Jan Dittberner',
        'Copyright © 2012 Nicolas Dandrimont',
        ])
__license__ = 'MIT'

import os
import shutil

from debexpo.tests import TestController, url
import pylons.test

class TestUploadController(TestController):

    def setUp(self):
        self._setup_models()
        self._setup_example_user()
        app_config = pylons.test.pylonsapp.config
        shutil.rmtree(app_config['debexpo.upload.incoming'])
        os.makedirs(os.path.join(app_config['debexpo.upload.incoming'], 'pub'))

    def tearDown(self):
        self._remove_example_user()
        app_config = pylons.test.pylonsapp.config

    def test_get(self):
        """
        Tests whether requests where method != PUT are rejected with error code 405.
        """
        response = self.app.get(url(controller='upload', action='index',
                                    filename='testname.dsc'), expect_errors=True)

        self.assertEqual(response.status_int, 405)

    def test_upload_wrong_extension(self):
        """
        Tests whether uploads of an unknown file extensions are rejected with error code 403.
        """
        response = self.app.put(url(controller='upload', action='index',
                                    filename='testname.unknown'),
                                expect_errors=True)

        self.assertEqual(response.status_int, 403)

    def test_upload_successful(self):
        """
        Tests whether uploads with sane file extensions and authorization are successful.
        """
        extensions = ('dsc', 'changes', 'deb', 'tar.gz', 'tar.bz2', 'tar.xz')

        for extension in extensions:
            filename = 'testfile.%s' % extension
            response = self.app.put(url(controller='upload', action='index',
                                        filename=filename),
                                    params='contents', expect_errors=False)

            self.assertEqual(response.status_int, 200)

            app_config = pylons.test.pylonsapp.config
            self.assertTrue(os.path.isfile(os.path.join(app_config['debexpo.upload.incoming'], 'pub',
                                                        filename)))

            self.assertEqual(file(os.path.join(app_config['debexpo.upload.incoming'], 'pub',
                                               filename)).read(), 'contents')

    def test_reupload_disallowed(self):
        """
        Tests whether uploading a file twice is disallowed.
        """
        filename = 'testfile.dsc'
        response = self.app.put(url(controller='upload', action='index',
                                    filename=filename),
                                params='contents', expect_errors=False)

        self.assertEqual(response.status_int, 200)

        response = self.app.put(url(controller='upload', action='index',
                                    filename=filename),
                                params='contents', expect_errors=True)

        self.assertEqual(response.status_int, 403)

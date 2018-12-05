# -*- coding: utf-8 -*-
#
#   test_upload.py — UploadController test cases
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
UploadController test cases.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import os
import base64

from debexpo.tests import TestController, url
import pylons.test


class TestUploadController(TestController):

    def __init__(self, *args, **kwargs):
        """
        Sets up database with data to provide a database to test.
        """
        TestController.__init__(self, *args, **kwargs)

    def setUp(self):
        self._setup_models()
        self._setup_example_user()
        self.incoming = pylons.test.pylonsapp.config['debexpo.upload.incoming']
        if not os.path.isdir(os.path.join(pylons.test.pylonsapp.config['debexpo.upload.incoming'], 'pub')):
            os.makedirs(os.path.join(pylons.test.pylonsapp.config['debexpo.upload.incoming'], 'pub'))

    def tearDown(self):
        self._remove_example_user()
        pylons.test.pylonsapp.config['debexpo.upload.incoming'] = self.incoming

    def testGetRequest(self):
        """
        Tests whether requests where method != PUT are rejected with error code
        405.
        """
        response = self.app.get(url(controller='upload',
                                    action='index',
                                    filename='testname.dsc'),
                                expect_errors=True)

        self.assertEqual(response.status_int, 405)

    def testExtensionNotAllowed(self):
        """
        Tests whether uploads of an unknown file extensions are rejected with
        error code 403.
        """
        response = self.app.put(url(controller='upload', action='index',
                                    filename='testname.unknown'),
                                expect_errors=True)

        self.assertEqual(response.status_int, 403)

    def testSuccessfulUpload(self):
        """
        Tests whether uploads with sane file extensions and authorization are
        successful.
        """
        response = self.app.put(url(
            controller='upload', action='index',
            filename='testfile2.dsc'),
            params='contents', expect_errors=False)

        self.assertEqual(response.status_int, 200)

        app_config = pylons.test.pylonsapp.config
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    app_config['debexpo.upload.incoming'],
                    'pub',
                    'testfile2.dsc')))

        self.assertEqual(
            file(
                os.path.join(
                    app_config['debexpo.upload.incoming'],
                    'pub',
                    'testfile2.dsc')).read(),
            'contents')

        if os.path.isfile(os.path.join(app_config['debexpo.upload.incoming'],
                                       'pub', 'testfile2.dsc')):
            os.remove(os.path.join(app_config['debexpo.upload.incoming'],
                                   'pub', 'testfile2.dsc'))

    def testDuplicatedUpload(self):
        """
        Tests whether a re-uploads of the same file failed with error code 403.
        """
        response = self.app.put(url(
            controller='upload', action='index',
            filename='testfile.dsc'),
            params='contents', expect_errors=False)

        self.assertEqual(response.status_int, 200)

        response = self.app.put(url(
            controller='upload', action='index',
            filename='testfile.dsc'),
            params='contents', expect_errors=True)

        self.assertEqual(response.status_int, 403)

        app_config = pylons.test.pylonsapp.config

        if os.path.isfile(os.path.join(app_config['debexpo.upload.incoming'],
                                       'pub', 'testfile.dsc')):
            os.remove(os.path.join(app_config['debexpo.upload.incoming'],
                                   'pub', 'testfile.dsc'))

    def testUploadWithoutConfig(self):
        """
        Tests whether an uploads without debexpo.upload.incoming fails.
        """
        incoming = pylons.test.pylonsapp.config.pop('debexpo.upload.incoming')

        response = self.app.put(url(
            controller='upload', action='index',
            filename='testfile.dsc'),
            params='contents', expect_errors=True)


        self.assertEqual(response.status_int, 500)

    def testUploadNonexistantQueue(self):
        """
        Tests whether an uploads with an nonexistant queue fails.
        """
        app_config = pylons.test.pylonsapp.config
        app_config['debexpo.upload.incoming'] = '/nonexistant'

        response = self.app.put(url(
            controller='upload', action='index',
            filename='testfile.dsc'),
            params='contents', expect_errors=True)

        self.assertEqual(response.status_int, 500)

    def testUploadNonwritableQueue(self):
        """
        Tests whether an uploads with an nonwritable queue fails.
        """
        app_config = pylons.test.pylonsapp.config
        app_config['debexpo.upload.incoming'] = '/proc/sys'

        response = self.app.put(url(
            controller='upload', action='index',
            filename='testfile.dsc'),
            params='contents', expect_errors=True)

        self.assertEqual(response.status_int, 500)

# -*- coding: utf-8 -*-
#
#   test_upload.py — UploadController test cases
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
UploadController test cases.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import os

from debexpo.tests import TestController, url
import pylons.test


class TestUploadController(TestController):

    _CHANGES_CONTENT = """
Format: 1.8
Date: Tue, 12 Mar 2019 17:31:31 +0100
Source: vitetris
Binary: vitetris vitetris-dbgsym
Architecture: source amd64
Version: 0.58.0-1
Distribution: unstable
Urgency: medium
Maintainer: Baptiste BEAUPLAT <lyknode@cilg.org>
Changed-By: Baptiste BEAUPLAT <lyknode@cilg.org>
Description:
 vitetris   - Virtual terminal *tris clone
Changes:
 vitetris (0.58.0-1) unstable; urgency=medium
 .
   * New upstream version 0.58.0
Checksums-Sha1:
 aaaa 1261 vitetris_0.58.0-1.dsc
Checksums-Sha256:
 aaaa 1261 vitetris_0.58.0-1.dsc
Files:
 aaaa 1261 games optional vitetris_0.58.0-1.dsc
"""

    def __init__(self, *args, **kwargs):
        """
        Sets up database with data to provide a database to test.
        """
        TestController.__init__(self, *args, **kwargs)

    def setUp(self):
        self._setup_models()
        self._setup_example_user()
        self.incoming = pylons.test.pylonsapp.config['debexpo.upload.incoming']
        if not os.path.isdir(os.path.join(
                pylons.test.pylonsapp.config['debexpo.upload.incoming'],
                'pub')):
            os.makedirs(os.path.join(
                pylons.test.pylonsapp.config['debexpo.upload.incoming'], 'pub'))

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
        # First upload allowed
        response = self.app.put(url(
            controller='upload', action='index',
            filename='vitetris_0.58.0-1.dsc'),
            params='contents', expect_errors=False)

        self.assertEqual(response.status_int, 200)

        # Upload a file not referenced allowed
        response = self.app.put(url(
            controller='upload', action='index',
            filename='testfile.changes'),
            params=self._CHANGES_CONTENT, expect_errors=False)

        self.assertEqual(response.status_int, 200)

        # Second upload denined (.changes)
        response = self.app.put(url(
            controller='upload', action='index',
            filename='testfile.changes'),
            params=self._CHANGES_CONTENT, expect_errors=True)

        self.assertEqual(response.status_int, 403)

        # Second upload denined (others)
        response = self.app.put(url(
            controller='upload', action='index',
            filename='vitetris_0.58.0-1.dsc'),
            params='contents', expect_errors=True)

        self.assertEqual(response.status_int, 403)

        app_config = pylons.test.pylonsapp.config

        for filename in (os.path.join(app_config['debexpo.upload.incoming'],
                                      'pub', 'vitetris_0.58.0-1.dsc'),
                         os.path.join(app_config['debexpo.upload.incoming'],
                                      'pub', 'testfile.changes')):
            if os.path.isfile(filename):
                os.remove(filename)

    def testUploadWithoutConfig(self):
        """
        Tests whether an uploads without debexpo.upload.incoming fails.
        """
        pylons.test.pylonsapp.config.pop('debexpo.upload.incoming')

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

# -*- coding: utf-8 -*-
#
#   test_upload.py — UploadController test cases
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
UploadController test cases.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import os
import base64
import md5
from datetime import datetime

from debexpo.lib.base import config
from debexpo.tests import *
from debexpo.model import meta, import_all_models
from debexpo.model.users import User
import pylons.test

class TestUploadController(TestController):

    def __init__(self, *args, **kwargs):
        """
        Sets up database with data to provide a database to test.
        """
        TestController.__init__(self, *args, **kwargs)

        # Keep this so tests don't have to constantly create it.
        self.emailpassword = base64.encodestring('email@email.com:password')[:-1]

    def setUp(self):
        # Since we are using a sqlite database in memory (at least that's what the default in
        # test.ini is), we need to create all the tables necessary. So let's import all the models
        # and create all the tables.
        import_all_models()
        meta.metadata.create_all(bind=meta.engine)

        # Create a test user and save it.
        user = User(name='Test user', email='email@email.com',
                    password=md5.new('password').hexdigest(), lastlogin=datetime.now())

        meta.session.add(user)
        meta.session.commit()

    def tearDown(self):
        meta.session.query(User).delete()

    def testGetRequest(self):
        """
        Tests whether requests where method != PUT are rejected with error code 405.
        """
        response = self.app.get(url(controller='upload', action='index',
                                    filename='testname.dsc'), expect_errors=True)

        self.assertEqual(response.status_int, 405)

    def testNoAuthorization(self):
        """
        Tests whether requests where the "Authorization" header is missing are rejected with
        error code 401 and whether the "WWW-Authenticate" header is sent in the response with
        the correct "realm" syntax.
        """
        response = self.app.put(url(controller='upload', action='index',
                                    filename='testname.dsc'), expect_errors=True)

        self.assertEqual(response.status_int, 401)

        authenticate = response.www_authenticate

        self.assertNotEqual(authenticate, None)

        self.assertEquals(authenticate[0], 'Basic')
        self.assertTrue('realm' in authenticate[1])

    def testFalseAuthentication(self):
        """
        Tests whether false authentication details returns a 401 error code.
        """
        wrongemailpassword = base64.encodestring('email@email.com:wrongpassword')[:-1]

        response = self.app.put(url(controller='upload', action='index',
                                    filename='testname.dsc'),
            headers={'Authorization' : 'Basic %s' % wrongemailpassword}, expect_errors=True)

        self.assertEqual(response.status_int, 401)

    def testTrueAuthentication(self):
        """
        Tests whether true authentication details returns a nicer error code.
        """
        response = self.app.put(url(controller='upload', action='index',
                                    filename='testfile1.dsc'),
            headers={'Authorization' : 'Basic %s' % self.emailpassword}, expect_errors=True)

        self.assertNotEqual(response.status_int, 401)
        config = pylons.test.pylonsapp.config

        if os.path.isfile(os.path.join(config['debexpo.upload.incoming'], 'testfile1.dsc')):
            os.remove(os.path.join(config['debexpo.upload.incoming'], 'testfile1.dsc'))

    def testExtensionNotAllowed(self):
        """
        Tests whether uploads of an unknown file extensions are rejected with error code 403.
        """
        response = self.app.put(url(controller='upload', action='index',
                                    filename='testname.unknown'),
            headers={'Authorization' : 'Basic %s' % self.emailpassword}, expect_errors=True)

        self.assertEqual(response.status_int, 403)

    def testSuccessfulUpload(self):
        """
        Tests whether uploads with sane file extensions and authorization are successful.
        """
        response = self.app.put(url(controller='upload', action='index',
                                    filename='testfile2.dsc'),
            headers={'Authorization' : 'Basic %s' % self.emailpassword},
            params='contents', expect_errors=True)

        self.assertEqual(response.status_int, 200)

        config = pylons.test.pylonsapp.config
        self.assertTrue(os.path.isfile(os.path.join(config['debexpo.upload.incoming'],
                                                    'testfile2.dsc')))

        self.assertEqual(file(os.path.join(config['debexpo.upload.incoming'],
                                           'testfile2.dsc')).read(), 'contents')

        if os.path.isfile(os.path.join(config['debexpo.upload.incoming'], 'testfile2.dsc')):
            os.remove(os.path.join(config['debexpo.upload.incoming'], 'testfile2.dsc'))

# -*- coding: utf-8 -*-
#
#   test_debian.py — DebianController test cases
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
DebianController test cases.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import os

from debexpo.tests import *
import pylons.test


class TestDebianController(TestController):

    def testFileNotFound(self):
        """
        Tests whether the response to a GET request on a non-existent file is 404.
        """
        response = self.app.get(url(controller='debian', action='index',
                                    filename='file_does_not_exist'), expect_errors=True)

        self.assertEqual(response.status_int, 404)

    def testFileFound(self):
        """
        Tests whether files that do exist in the repository are correctly returned.
        """
        file = os.path.join(pylons.test.pylonsapp.config['debexpo.repository'], 'test_file')

        f = open(file, 'w')
        f.write('test content')
        f.close()

        response = self.app.get(url(controller='debian', action='index', filename='test_file'))

        self.assertEqual(response.status_int, 200)

        self.assertEqual(response.normal_body, 'test content')

        # Remove temporary file.
        if os.path.isfile(file):
            os.remove(file)

    def testDscFileFound(self):
        """
        Tests whether the correct content-type for dsc files is returned.
        """
        file = os.path.join(pylons.test.pylonsapp.config['debexpo.repository'], 'test.dsc')

        f = open(file, 'w')
        f.write('test')
        f.close()

        response = self.app.get(url(controller='debian', action='index', filename='test.dsc'))
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/plain')

        # remove temporary file
        if os.path.isfile(file):
            os.remove(file)

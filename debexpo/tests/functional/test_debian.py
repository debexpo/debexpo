# -*- coding: utf-8 -*-
#
#   test_debian.py — DebianController test cases
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
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
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import os

from debexpo.lib.base import config
from debexpo.tests import *

class TestDebianController(TestController):

    def testFileNotFound(self):
        """
        Tests whether the response to a GET request on a non-existent file is 404.
        """
        response = self.app.get(url_for(controller='debian', filename='file_does_not_exist'), expect_errors=True)

        self.assertEqual(response.status, 404)

    def testFileFound(self):
        """
        Tests whether files that do exist in the repository are correctly returned.
        """
        file = os.path.join(config['debexpo.repository'], 'test_file')

        f = open(file, 'w')
        f.write('test content')
        f.close()

        response = self.app.get(url_for(controller='debian', filename='test_file'))

        self.assertEqual(response.status, 200)

        self.assertEqual(response.normal_body, 'test content')

        # Remove temporary file.
        if os.path.isfile(file):
            os.remove(file)

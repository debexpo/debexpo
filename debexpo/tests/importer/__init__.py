# -*- coding: utf-8 -*-
#
#   test_upload.py — UploadController test cases
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2018 Baptiste BEAUPLAT <lyknode@cilg.org>
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

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2018 Baptiste BEAUPLAT'
__license__ = 'MIT'

from debexpo.tests import TestController, url

class TestImporterController(TestController):
    """
    Toolbox for importer tests

    This class setup an environment for package to be imported in and ensure
    cleanup afterward.
    """

    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)

    def setUp(self):
        self._setup_models()
        self._setup_example_user(gpg=True)

    def tearDown(self):
        self._cleanup_mailbox()
        self._cleanup_repo()

    def _cleanup_mailbox(self):
        """Delete mailbox file"""

    def _cleanup_repo(self):
        """Delete all files present in repo directory"""

    def import_package(self, package_dir):
        """Run debexpo importer on package_dir/*.changes"""

    def assert_importer_failed(self):
        """Assert that the importer has failed"""

    def assert_importer_succeeded(self):
        """Assert that the importer has succeeded"""

    def assert_no_email(self):
        """Assert that the importer has not generated any email"""

    def assert_email_with(self, search_text):
        """
        Assert that the imported would have sent a email to the uploader
        containing search_text
        """

    def assert_package_count(self, package, version ,count):
        """
        Assert that a package appears count times in debexpo

        If count > 0, this method with also assert that the package is present
        in debexpo repository.
        """


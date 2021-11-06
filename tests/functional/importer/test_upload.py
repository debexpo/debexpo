#   test_upload.py — functional tests for package upload
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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

from logging import getLogger
import os
from tempfile import TemporaryDirectory

from django.conf import settings
from django.urls import reverse

from tests import TestController

log = getLogger(__name__)


class TestUploadController(TestController):

    _UNSIGNED_CHANGES_CONTENT = """
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
 4a756ca07e9487f482465a99e8286abc86ba4dc7 1261 vitetris_0.58.0-1.dsc
Checksums-Sha256:
 d1b2a59fbea7e20077af9f91b27e95e865061b270be03ff539ab3b73587882e8 1261 vitetris_0.58.0-1.dsc
Files:
 98bf7d8c15784f0a3d63204441e1e2aa 1261 games optional vitetris_0.58.0-1.dsc
"""  # noqa: E501
    _CHANGES_CONTENT = f"""
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512
{_UNSIGNED_CHANGES_CONTENT}-----BEGIN PGP SIGNATURE-----

iHUEARYKAB0WIQRVkwbu4cjBst0cc7HENHgc6HHz3wUCXfjpNAAKCRDENHgc6HHz
3yJ9AQC0U9bahPO/TH/4ULdsnBd0ECHCG6wJmvBBrrEsfxHjhwD9GlqAs6pTyoYZ
fC0rs1ly7CQ7ZQN441ZE3csnK69gzwc=
=1nnA
-----END PGP SIGNATURE-----
"""
    _CHANGES_CONTENT_SUBKEY = f"""
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512
{_UNSIGNED_CHANGES_CONTENT}-----BEGIN PGP SIGNATURE-----

iHUEARYKAB0WIQSzz3sz+AdjONtPqA6HkZKDEXU71wUCXgkR1wAKCRCHkZKDEXU7
19RiAQDcC+i0jXdCo2+dY1QTtBY3072BhBD3uq5dT9XPaqYvOAEA8Pk7FdZReoLw
C7NQGzfRMFLSPxIHVzhHvJUo6vNZ+AA=
=FCEl
-----END PGP SIGNATURE-----
"""

    def setUp(self):
        self._setup_example_user(gpg=True)
        self.spool = TemporaryDirectory()
        self.old_spool = getattr(settings, 'UPLOAD_SPOOL', None)
        settings.UPLOAD_SPOOL = self.spool.name

    def tearDown(self):
        self._remove_example_user()
        settings.UPLOAD_SPOOL = self.old_spool

    def testGetRequest(self):
        """
        Tests whether requests where method != PUT are rejected with error code
        405.
        """
        response = self.client.get(reverse('upload', args=['testname.dsc']))

        self.assertEqual(response.status_code, 405)

    def testExtensionNotAllowed(self):
        """
        Tests whether uploads of an unknown file extensions are rejected with
        error code 403.
        """
        response = self.client.put(reverse('upload', args=['testname.unknown']))

        self.assertEqual(response.status_code, 403)

    def testSuccessfulUpload(self):
        """
        Tests whether uploads with sane file extensions and authorization are
        successful.
        """
        response = self.client.put(reverse('upload', args=['testfile2.dsc']),
                                   data='contents')

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    settings.UPLOAD_SPOOL,
                    'incoming',
                    'testfile2.dsc')))

        with open(
            os.path.join(
                settings.UPLOAD_SPOOL,
                'incoming',
                'testfile2.dsc')) as fd:
            self.assertEqual(fd.read(), 'contents')

        if os.path.isfile(os.path.join(settings.UPLOAD_SPOOL,
                                       'incoming', 'testfile2.dsc')):
            os.remove(os.path.join(settings.UPLOAD_SPOOL,
                                   'incoming', 'testfile2.dsc'))

    def testDuplicatedUpload(self, with_subkey=False):
        """
        Tests whether a re-uploads of the same file failed with error code 403.
        """

        # Malicous changes does not break upload
        response = self.client.put(reverse(
            'upload',
            args=['plop.changes']),
            data='contents')

        self.assertEqual(response.status_code, 200)

        # Invalid changes does not break upload
        response = self.client.put(reverse(
            'upload',
            args=['plop.changes']),
            data=self._UNSIGNED_CHANGES_CONTENT.replace('Source: vitetris\n',
                                                        ''))

        self.assertEqual(response.status_code, 200)

        # First upload allowed
        response = self.client.put(reverse(
            'upload',
            args=['vitetris_0.58.0-1.dsc']),
            data='contents')

        self.assertEqual(response.status_code, 200)

        # Second upload allowed
        response = self.client.put(reverse(
            'upload',
            args=['vitetris_0.58.0-1.dsc']),
            data='contents')

        self.assertEqual(response.status_code, 200)

        if with_subkey:
            data = self._CHANGES_CONTENT_SUBKEY
        else:
            data = self._CHANGES_CONTENT

        # Upload a file not referenced allowed
        response = self.client.put(reverse(
            'upload',
            args=['testfile.changes']),
            data=data)

        self.assertEqual(response.status_code, 200)

        # Second upload denined (.changes)
        response = self.client.put(reverse(
            'upload',
            args=['testfile.changes']),
            data=data)

        self.assertEqual(response.status_code, 403)

        # Second upload denined (others)
        response = self.client.put(reverse(
            'upload',
            args=['vitetris_0.58.0-1.dsc']),
            data='contents')

        self.assertEqual(response.status_code, 403)

        # Next upload allowed
        response = self.client.put(reverse(
            'upload',
            args=['vitetris_0.58.0-2.dsc']),
            data='contents')

        self.assertEqual(response.status_code, 200)

        for filename in (os.path.join(settings.UPLOAD_SPOOL,
                                      'incoming', 'vitetris_0.58.0-1.dsc'),
                         os.path.join(settings.UPLOAD_SPOOL,
                                      'incoming', 'testfile.changes')):
            if os.path.isfile(filename):
                os.remove(filename)

        if not with_subkey:
            self.testDuplicatedUpload(True)

    def testUploadNonwritableQueue(self):
        """
        Tests whether an uploads with an nonwritable queue fails.
        """
        settings.UPLOAD_SPOOL = '/proc/sys'

        response = self.client.put(reverse(
            'upload',
            args=['testfile.dsc']),
            data='contents')

        self.assertEqual(response.status_code, 500)

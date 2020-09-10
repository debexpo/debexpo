#   test_origin.py - unit testing for Origin
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2020 Baptiste Beauplat <lyknode@cilg.org>
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

from tempfile import TemporaryDirectory
from unittest import TestCase
from os.path import join

from debexpo.tools.debian.origin import Origin, ExceptionOrigin
from debexpo.tools.files import CheckSumedFile
from debexpo.tools.clients import ExceptionClient

_HTOP_SIG_SHA256 = \
    'dcd37ff7c12ad4e61525d6a5661721201817f380a278c03ba71f8cc919a93361'
_HTOP_ORIG_SHA256 = \
    'becdd93eb41c949750ef2d923d6f7f6157c0d926ebd52d2472a45507eb791d13'
_BAD_SHA256 = \
    '577115e9ba818b7ea28f2f6aa54229cff4db39c718a320f4a4d0679cb006dee7'
_TMUX_ORIG_SHA256 = \
    '7f6bf335634fafecff878d78de389562ea7f73a7367f268b66d37ea13617a2ba'
_0AD_ORIG_SHA256 = \
    'fdbf774637252dbedf339fbe29b77d7d585ab53a9a5ddede56dd7b8fda66d8ac'


class TestOrigin(TestCase):
    def _check_download(self, origin_files):
        for sumed_file in origin_files:
            sumed_file.validate()

        return True

    def _gen_orig(self, package, version, orig_sha, sig_sha, method='gz'):
        origins = []

        orig_file = '{}_{}.orig.tar.{}'.format(package, version, method)
        sig_file = '{}.asc'.format(orig_file)

        for (filename, sha) in [(orig_file, orig_sha), (sig_file, sig_sha)]:
            if sha is not None:
                sumed_file = CheckSumedFile(join(self.queue.name, filename))
                sumed_file.add_checksum('sha256', sha)
                origins.append(sumed_file)

        return origins

    def setUp(self):
        self.queue = TemporaryDirectory()

    #
    # Tests for Origin.exists()
    #
    def test_package_exists(self):
        package = Origin('htop', '2.2', 'main', None)

        package.validate(self._gen_orig('htop', '2.2', _HTOP_ORIG_SHA256,
                                        _HTOP_SIG_SHA256))

        self.assertFalse(package.is_new)

    def test_package_dont_exists(self):
        package = Origin('hello', '2.9.42', 'main', None)

        package.validate(self._gen_orig('hello', '2.9.42', _BAD_SHA256,
                                        None))

        self.assertTrue(package.is_new)

    #
    # Tests for Origin.use_same_orig()
    #
    # Test cases:
    # |----+----------+----------+--------|
    # | #  | orig     | sig      | Result |
    # |----+----------+----------+--------|
    # | 1  | None     |          | True   |
    # | 2  | Match    |          | True   |
    # | 3  | Local    |          | True   |
    # | 4  | Official |          | True   |
    # | 5  | Mismatch |          | False  |
    # | 6  |          | None     | True   |
    # | 7  |          | Match    | True   |
    # | 8  |          | Local    | True   |
    # | 9  |          | Official | True   |
    # | 10 |          | Mismatch | False  |
    # |----+----------+----------+--------|
    #

    def _assert_orig_success(self, package, version,
                             sha_orig, sha_sig, method='gz'):
        orig = self._gen_orig(package, version, sha_orig, sha_sig, method)
        package = Origin(package, version, 'main', None)

        package.validate(orig)

    def _assert_orig_failed(self, package, version,
                            sha_orig, sha_sig, method='gz'):
        self.assertRaises(ExceptionOrigin, self._assert_orig_success, package,
                          version, sha_orig, sha_sig, method)

    def _download_origin(self, package, version,
                         sha_orig, sha_sig, method='gz'):
        orig = self._gen_orig(package, version, sha_orig, sha_sig, method)
        package = Origin(package, version, 'main', self.queue.name)

        package.fetch(orig)
        self._check_download(orig)

    def test_same_orig_1_6(self):
        self._assert_orig_success('dpkg', '1.19.5', None, None)

    def test_same_orig_3(self):
        self._assert_orig_success('dpkg', '1.19.5', _BAD_SHA256, None)

    def test_same_orig_8(self):
        self._assert_orig_success('dpkg', '1.19.5', None, _BAD_SHA256)

    def test_same_orig_2_7(self):
        self._assert_orig_success('htop', '2.2.0', _HTOP_ORIG_SHA256,
                                  _HTOP_SIG_SHA256)

    def test_same_orig_4(self):
        self._assert_orig_success('htop', '2.2.0', None, _HTOP_SIG_SHA256)

    def test_same_orig_5(self):
        self._assert_orig_failed('htop', '2.2.0', _BAD_SHA256, _HTOP_SIG_SHA256)

    def test_same_orig_9(self):
        self._assert_orig_success('htop', '2.2.0', _HTOP_ORIG_SHA256, None)

    def test_same_orig_10(self):
        self._assert_orig_failed('htop', '2.2.0',
                                 _HTOP_ORIG_SHA256, _BAD_SHA256)

    # #
    # # Tests for Origin.download_orig()
    # #
    def test_download_native(self):
        self._download_origin('dpkg', '1.19.5', None, None)

    def test_download_orig(self):
        self._download_origin('tmux', '2.8', _TMUX_ORIG_SHA256, None)

    def test_download_orig_with_sig(self):
        self._download_origin('htop', '2.2.0', _HTOP_ORIG_SHA256,
                              _HTOP_SIG_SHA256)

    def test_download_oversized(self):
        self.assertRaises(ExceptionClient, self._download_origin, '0ad-data',
                          '0.0.23', _0AD_ORIG_SHA256, None, method='xz')

    def test_download_dont_exists(self):
        self._download_origin('this-package-should-not-exist', '42.42.42', None,
                              None)

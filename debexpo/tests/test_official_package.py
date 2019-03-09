# -*- coding: utf-8 -*-
#
#   test_gitstorage.py - unit testing for GitStorage class
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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
__copyright__ = 'Copyright © 2019 Baptiste BEAUPLAT'
__license__ = 'MIT'

import pylons.test

from debexpo.lib.official_package import OfficialPackage, OverSized
from debexpo.lib.utils import sha256sum
from nose.tools import raises
from os import makedirs, getcwd, chdir
from os.path import isfile, isdir, join
from shutil import rmtree
from unittest import TestCase

_HTOP_SIG_SHA256 = 'dcd37ff7c12ad4e61525d6a5661721201817f380a278c03ba71f8cc919a93361'
_HTOP_ORIG_SHA256 = 'becdd93eb41c949750ef2d923d6f7f6157c0d926ebd52d2472a45507eb791d13'
_BAD_SHA256 = '577115e9ba818b7ea28f2f6aa54229cff4db39c718a320f4a4d0679cb006dee7'
_TMUX_ORIG_SHA256 = '7f6bf335634fafecff878d78de389562ea7f73a7367f268b66d37ea13617a2ba'


class TestOfficialPackage(TestCase):
    def _check_download(self, package, version, orig_sha, sig_sha):
        orig_file = '{}_{}.orig.tar.gz'.format(package, version)
        sig_file = '{}.asc'.format(orig_file)

        for (filename, sha) in [(orig_file, orig_sha), (sig_file, sig_sha)]:
            if sha is not None:
                if not isfile(filename):
                    return False
                if sha256sum(filename) != sha:
                    return False
            else:
                if isfile(filename):
                    return False

        return True

    def _gen_dsc(self, package, version, orig_sha, sig_sha):
        orig_file = '{}_{}.orig.tar.gz'.format(package, version)
        sig_file = '{}.asc'.format(orig_file)
        dsc = {'Checksums-Sha256': []}

        for (filename, sha) in [(orig_file, orig_sha), (sig_file, sig_sha)]:
            if sha is not None:
                dsc['Checksums-Sha256'].append({'name': filename,
                                                'sha256': sha})

        return dsc

    def setUp(self):
        self.old_dir = getcwd()
        self.work_dir = join(self.old_dir, 'debexpo-dl')

        if not isdir(self.work_dir):
            makedirs(self.work_dir)

        chdir(self.work_dir)

    def tearDown(self):
        if isdir(self.work_dir):
            rmtree(self.work_dir)

        chdir(self.old_dir)

    #
    # Tests for OfficialPackage.exists()
    #
    def test_package_exists(self):
        package = OfficialPackage('hello', '2.10-42')

        self.assertTrue(package.exists())

    def test_package_dont_exists(self):
        package = OfficialPackage('hello', '2.9.42-42')

        self.assertFalse(package.exists())

    #
    # Tests for OfficialPackage.use_same_orig()
    #
    # Test cases:
    # |----+----------+----------+--------|
    # | #  | orig     | sig      | Result |
    # |----+----------+----------+--------|
    # | 1  | None     |          | True   |
    # | 2  | Match    |          | True   |
    # | 3  | Local    |          | False  |
    # | 4  | Official |          | False  |
    # | 5  | Mismatch |          | False  |
    # | 6  |          | None     | True   |
    # | 7  |          | Match    | True   |
    # | 8  |          | Local    | False  |
    # | 9  |          | Official | False  |
    # | 10 |          | Mismatch | False  |
    # |----+----------+----------+--------|
    #
    def test_same_orig_1_6(self):
        package = OfficialPackage('dpkg', '1.19.5')

        dsc = self._gen_dsc('dpkg', '1.19.5', None, None)
        (result, outcome) = package.use_same_orig(dsc)

        self.assertTrue(result)

    def test_same_orig_3(self):
        package = OfficialPackage('dpkg', '1.19.5')

        dsc = self._gen_dsc('dpkg', '1.19.5', _BAD_SHA256, None)
        (result, outcome) = package.use_same_orig(dsc)

        self.assertFalse(result)

    def test_same_orig_8(self):
        package = OfficialPackage('dpkg', '1.19.5')

        dsc = self._gen_dsc('dpkg', '1.19.5', None, _BAD_SHA256)
        (result, outcome) = package.use_same_orig(dsc)

        self.assertFalse(result)

    def test_same_orig_2_7(self):
        package = OfficialPackage('htop', '2.2.0')

        dsc = self._gen_dsc('htop', '2.2.0', _HTOP_ORIG_SHA256,
                            _HTOP_SIG_SHA256)
        (result, outcome) = package.use_same_orig(dsc)

        self.assertTrue(result)

    def test_same_orig_4(self):
        package = OfficialPackage('htop', '2.2.0')

        dsc = self._gen_dsc('htop', '2.2.0', None, _HTOP_SIG_SHA256)
        (result, outcome) = package.use_same_orig(dsc)

        self.assertFalse(result)

    def test_same_orig_5(self):
        package = OfficialPackage('htop', '2.2.0')

        dsc = self._gen_dsc('htop', '2.2.0', _BAD_SHA256, _HTOP_SIG_SHA256)
        (result, outcome) = package.use_same_orig(dsc)

        self.assertFalse(result)

    def test_same_orig_9(self):
        package = OfficialPackage('htop', '2.2.0')

        dsc = self._gen_dsc('htop', '2.2.0', _HTOP_ORIG_SHA256, None)
        (result, outcome) = package.use_same_orig(dsc)

        self.assertFalse(result)

    def test_same_orig_10(self):
        package = OfficialPackage('htop', '2.2.0')

        dsc = self._gen_dsc('htop', '2.2.0', _HTOP_ORIG_SHA256, _BAD_SHA256)
        (result, outcome) = package.use_same_orig(dsc)

        self.assertFalse(result)

    #
    # Tests for OfficialPackage.download_orig()
    #
    def test_download_native(self):
        package = OfficialPackage('dpkg', '1.19.5')

        package.download_orig()
        self.assertTrue(self._check_download('dpkg', '1.19.5', None, None))

    def test_download_orig(self):
        package = OfficialPackage('tmux', '2.8')

        package.download_orig()
        self.assertTrue(self._check_download('tmux', '2.8', _TMUX_ORIG_SHA256,
                                             None))

    def test_download_orig_with_sig(self):
        package = OfficialPackage('htop', '2.2.0')

        package.download_orig()
        self.assertTrue(self._check_download('htop', '2.2.0', _HTOP_ORIG_SHA256,
                                             _HTOP_SIG_SHA256))

    @raises(OverSized)
    def test_download_oversized(self):
        package = OfficialPackage('0ad-data', '0.0.23')

        package.download_orig()

    def test_download_dont_exists(self):
        package = OfficialPackage('this-package-should-not-exist', '42.42.42')

        package.download_orig()
        self.assertTrue(self._check_download('this-package-should-not-exist',
                                             '42.42.42', None, None))

    def test_download_wrong_mirror(self):
        app_config = pylons.test.pylonsapp.config
        old_mirror = app_config['debexpo.debian_mirror']
        app_config['debexpo.debian_mirror'] = 'http://nxdomain/'

        package = OfficialPackage('htop', '2.2.0')

        package.download_orig()
        self.assertTrue(self._check_download('htop', '2.2.0', None, None))

        app_config['debexpo.debian_mirror'] = old_mirror

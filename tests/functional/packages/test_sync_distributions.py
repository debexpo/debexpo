#   test_sync_distributions.py - functionnal test for sync_distributions command
#
#   This file is part of debexpo
#   https://salsa.debian.com/mentors.debian.net-team/debexpo
#
#   Copyright © 2023 Baptiste Beauplat <lyknode@debian.org>
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

from unittest.mock import patch
from os.path import abspath, dirname, join

from django.core.management import call_command, CommandError

from debexpo.packages.models import Distribution

from tests import TestController


class TestCommandSyncDistributions(TestController):
    REF_DISTS_ADDED = {
        'bookworm',
        'bookworm-backports',
        'bookworm-backports-sloppy',
        'bookworm-proposed-updates',
        'bookworm-security',
        'bookworm-updates',
        'bullseye-proposed-updates',
        'oldstable-updates',
        'stable-backports-sloppy',
        'stable-updates',
        'testing-backports',
        'testing-backports-sloppy',
        'testing-updates',
        'trixie',
        'trixie-backports',
        'trixie-backports-sloppy',
        'trixie-proposed-updates',
        'trixie-security',
        'trixie-updates',
    }
    REF_DISTS_DELETED = {
        'buster',
        'buster-backports',
        'buster-backports-sloppy',
        'buster-security',
        'buster-updates',
        'jessie',
        'jessie-backports',
        'jessie-backports-sloppy',
        'jessie-security',
        'jessie-updates',
        'squeeze',
        'squeeze-backports',
        'squeeze-backports-sloppy',
        'squeeze-security',
        'squeeze-updates',
        'stretch',
        'stretch-backports',
        'stretch-backports-sloppy',
        'stretch-security',
        'stretch-updates',
        'wheezy',
        'wheezy-backports',
        'wheezy-backports-sloppy',
        'wheezy-security',
        'wheezy-updates',
    }

    def _get_dists(self):
        return {str(dist) for dist in Distribution.objects.all()}

    def setUp(self):
        self.dists_before = self._get_dists()

    def _sync_distributions(self, args=None):
        if args is None:
            args = []

        with patch('distro_info._get_data_dir',
                   return_value=join(abspath(dirname(__file__)),
                                     'distro-info')):
            call_command(*(['sync_distributions', '--no-confirm'] + args))

    def _assert_sync(self, dists_added=None, dists_deleted=None):
        if dists_added is None:
            dists_added = self.REF_DISTS_ADDED

        if dists_deleted is None:
            dists_deleted = self.REF_DISTS_DELETED

        self.assertEquals(self._get_dists(),
                          (self.dists_before | dists_added) - dists_deleted)

    def test_sync_success(self):
        self._sync_distributions()
        self._assert_sync()

    def test_sync_no_changes(self):
        self._sync_distributions(['--dry-run'])
        self._assert_sync(set(), set())

    def test_sync_excluded(self):
        self._sync_distributions(['--exclude', '^bookworm$'])
        self._assert_sync(self.REF_DISTS_ADDED - {'bookworm'})

    def test_sync_no_create(self):
        self._sync_distributions(['--no-create'])
        self._assert_sync(set())

    def test_sync_no_cleanup(self):
        self._sync_distributions(['--no-cleanup'])
        self._assert_sync(self.REF_DISTS_ADDED, set())

    def test_sync_bad_vendor(self):
        with self.settings(DISTRO_INFO_VENDOR='RHEL'):
            with self.assertRaises(CommandError) as e:
                self.test_sync_success()

        self.assertIn('Failed to import module RhelDistroInfo',
                      str(e.exception))

#   test_proc.py - Unit testing for debexpo_exec
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright (c) 2022 Baptiste Beauplat <lyknode@debian.org>
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
Test cases for debexpo.tools.proc
"""

import tempfile

from glob import glob
from os import environ
from os.path import join

from tests import TestController

from debexpo.tools.proc import debexpo_exec


class TestDebexpoExec(TestController):
    def _assert_cleanup(self, **kwargs):
        exit_success = True

        with tempfile.TemporaryDirectory() as tmpdir:
            backup = tempfile.tempdir

            try:
                tempfile.tempdir = tmpdir
                output = debexpo_exec('/bin/sh', [
                    '-c', 'mkdir -v "$TMPDIR/mark"'
                ], **kwargs)
            except Exception:
                exit_success = False
            else:
                # On success, assert debexpo_exec tmpdir is created inside our
                # tmpdir
                self.assertIn(tmpdir, output)
            finally:
                tempfile.tempdir = backup
                # Always assert there is no left-over
                self.assertEqual(glob(join(tmpdir, '**')), [])

        return exit_success

    def test_tmpdir_cleanup_proc_ok(self):
        exit_success = self._assert_cleanup()
        self.assertTrue(exit_success)

    def test_tmpdir_cleanup_proc_fail(self):
        with self.settings(SUBPROCESS_TIMEOUT_SH=0):
            exit_success = self._assert_cleanup()
            self.assertFalse(exit_success)

    def test_tmpdir_cleanup_with_env(self):
        env = environ.copy()
        env['PATH'] = 'nope'

        exit_success = self._assert_cleanup(env=env)
        self.assertFalse(exit_success)

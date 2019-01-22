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

from debexpo.lib.gitstorage import GitStorage
from os import write, close
from os.path import isdir
from shutil import rmtree
from subprocess import Popen, PIPE, STDOUT
from tempfile import mkdtemp, mkstemp
from unittest import TestCase

class TestGitStorage(TestCase):
    def setUp(self):
        self.gitdir = mkdtemp()

    def tearDown(self):
        if isdir(self.gitdir):
            rmtree(self.gitdir)

    def _git(self, args):
        proc = Popen(['/usr/bin/git'] + args,
                stdout=PIPE, stderr=STDOUT, cwd=self.gitdir)
        (output, status) = proc.communicate()

        return (status, output)

    def _write_test_file(self):
        (fd, filename) = mkstemp(dir=self.gitdir)

        write(fd, "Hello world!\n")
        close(fd)

        return filename[len(self.gitdir) + 1:]

    def _git_count(self):
        (status, output) = self._git(['rev-list', '--all', '--count'])
        self.assertFalse(status)

        return int(output.rstrip())

    def _git_last_commited_files(self):
        (status, output) = self._git(['show', '--format=', '--name-only',
            'HEAD'])
        self.assertFalse(status)

        return output.split('\n')

    def test_init_new_repo(self):
        if isdir(self.gitdir):
            rmtree(self.gitdir)

        self.repo = GitStorage(self.gitdir)
        self.assertTrue(isdir(self.gitdir))

        self.assertEquals(self._git_count(), 1)

    def test_init_existing_repo(self):
        self.test_init_new_repo()

        self.repo = GitStorage(self.gitdir)
        self.assertEquals(self._git_count(), 1)

    def test_adding_new_files(self):
        self.test_init_new_repo()

        filename = self._write_test_file()
        self.repo.change([filename])

        self.assertEquals(self._git_count(), 2)
        self.assertTrue(filename in self._git_last_commited_files())

    def test_get_all_trees(self):
        self.test_adding_new_files()

        trees = self.repo.getAllTrees()
        self.assertEquals(len(trees), 2)

        (status, output) = self._git(['log', '--format=%T'])
        self.assertFalse(status)
        self.assertEquals(output.rstrip().split('\n'), trees)

    def test_get_last_tree(self):
        self.test_adding_new_files()

        tree = self.repo.getLastTree()

        (status, output) = self._git(['log', '--format=%T', 'HEAD~1..HEAD'])
        self.assertFalse(status)
        self.assertEquals(output.rstrip(), tree)

    def test_get_older_commits(self):
        self.test_adding_new_files()

        commits = self.repo.getOlderCommits()

        (status, output) = self._git(['log', '--format=%H', 'HEAD~1'])
        self.assertFalse(status)
        self.assertEquals(output.rstrip().split('\n'), commits)

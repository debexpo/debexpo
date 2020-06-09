#   test_gitstorage.py - unit testing for GitBackendDulwich class
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from debexpo.tools.gitstorage import GitBackendDulwich
from os import write, close, open, O_WRONLY
from os.path import isdir, join
from shutil import rmtree
from subprocess import check_output, STDOUT, CalledProcessError
from tempfile import mkdtemp, mkstemp
from unittest import TestCase


class TestGitBackendDulwich(TestCase):
    def setUp(self):
        self.gitdir = mkdtemp()

    def tearDown(self):
        if isdir(self.gitdir):
            rmtree(self.gitdir)

    def _git(self, args):
        try:
            output = check_output(['/usr/bin/git'] + args, stderr=STDOUT,
                                  cwd=self.gitdir, text=True)
        except CalledProcessError as e:
            return (e.returncode, e.output)

        return (0, output)

    def _write_test_file(self, text, filename=None):
        if filename:
            fd = open(join(self.gitdir, filename), O_WRONLY)
        else:
            (fd, filename) = mkstemp(dir=self.gitdir)

        write(fd, text.encode())
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

        self.repo = GitBackendDulwich(self.gitdir)
        self.assertTrue(isdir(self.gitdir))

        self.assertEquals(self._git_count(), 0)

    def test_init_existing_repo(self):
        self.test_init_new_repo()

        self.repo = GitBackendDulwich(self.gitdir)
        self.assertEquals(self._git_count(), 0)

    def test_adding_new_files(self, text="Hello World!\n"):
        self.test_init_new_repo()

        filename = self._write_test_file(text)
        self.repo.stage([filename])
        self.repo.commit()

        self.assertEquals(self._git_count(), 1)
        self.assertTrue(filename in self._git_last_commited_files())

    def test_get_all_trees(self):
        self.test_adding_new_files()

        trees = self.repo.getAllTrees()
        self.assertEquals(len(trees), 1)

        (status, output) = self._git(['log', '--format=%T'])
        self.assertFalse(status)
        self.assertEquals(output.rstrip().split('\n'),
                          [item.decode() for item in trees])

    def test_get_last_tree(self):
        self.test_adding_new_files()

        filename = self._write_test_file("Hello world!\n")
        self.repo.stage([filename])
        self.repo.commit()

        tree = self.repo.getLastTree()

        (status, output) = self._git(['log', '--format=%T', 'HEAD~1..HEAD'])
        self.assertFalse(status)
        self.assertEquals(output.rstrip(), tree.decode())

    def test_build_tree_diff(self):
        self.test_init_new_repo()

        filename = self._write_test_file("Hello world!\n")
        self.repo.stage([filename])
        self.repo.commit()

        changes = self.repo.buildTreeDiff()
        self.assertEquals('', changes.decode())

        self._write_test_file("New version\n", filename)
        self.repo.stage([filename])
        self.repo.commit()

        self.assertEquals(self._git_count(), 2)
        self.assertTrue(filename in self._git_last_commited_files())

        changes = self.repo.buildTreeDiff()
        self.assertTrue('-Hello world!\n+New version\n' in changes.decode())

        history = self.repo.getAllTrees()
        changes = self.repo.buildTreeDiff(history[0], history[1])
        self.assertTrue('-New version\n-\n+Hello world!\n' in changes.decode())

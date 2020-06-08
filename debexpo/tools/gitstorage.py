#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2012 Baptiste Mouterde <baptiste.mouterde@gmail.com>
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

from io import BytesIO
from os import makedirs, walk
from os.path import isdir, join, relpath
from logging import getLogger
from shutil import rmtree, copytree

from dulwich.repo import Repo
from dulwich.patch import write_tree_diff
from dulwich.index import get_unstaged_changes

fileToIgnore = []
log = getLogger(__name__)


class NoOlderContent(Exception):
    pass


class GitStorage():
    def __init__(self, git_storage_path):
        self.git_storage_path = git_storage_path

    def install(self, source):
        if not self.git_storage_path:
            return

        repository = join(self.git_storage_path,
                          source.control.source['Source'])
        git = GitBackendDulwich(repository)

        self._sync_source(source, repository)
        changes = self._list_files(repository)

        git.stage(changes, True)
        ref = git.commit()

        return ref

    # def remove(self, source):
    #     pass

    # def diff(self, upload_from, upload_to):
    #     pass

    def _sync_source(self, source, repository):
        dest = join(repository, 'sources')

        if isdir(dest):
            rmtree(dest)

        try:
            copytree(source.get_source_dir(), dest)
        except IOError:
            pass

    def _list_files(self, repository):
        dest = join(repository, 'sources')
        files = set()

        for (root, _, filenames) in walk(dest):
            for filename in filenames:
                fpath = join(root, filename)
                files.add(relpath(fpath, repository))

        return files


class GitBackendDulwich():
    def __init__(self, path):
        # Creating the repository
        if isdir(path):
            self.repo = Repo(path)
        else:
            makedirs(path)
            self.repo = Repo.init(path)

    # Only this function will be used on upload
    def stage(self, files, modified=False):
        """
        add files to the staging area before commit.

        ``files``
            a list of file to stage
        ``modified``
            if True, will stage pending modifications (useful for staging
            deletes)
        """
        if modified:
            files.update(set(get_unstaged_changes(self.repo.open_index(),
                                                  'sources')))

        if len(files) != 0:
            self.repo.stage(list(files))

    def commit(self):
        ref = self.repo.do_commit(b'this is so awesome that nobody will never '
                                  b'see it',
                                  committer=b'same here <foo@foo.foo>')

        return ref.decode()

    def buildTreeDiff(self, old_sha_tree=None, new_sha_tree=None):
        """
        creating files from the diff between 2 trees, it will be used in the
        code browser to get older version (walking on history)

        ``old_sha_tree``
            the tree that you want to compare from
        ``new_sha_tree``
            the tree that you want to compare to

        by default it returns last changed files
        """
        # set default for new_tree (current tree)
        if not new_sha_tree:
            new_sha_tree = self.getLastTree()

        # set default for old_tree (last tree)
        if not old_sha_tree:
            history = self.getAllTrees()
            if (len(history) > 1):
                old_sha_tree = history[1]
            else:
                old_sha_tree = history[0]

        # calculate changes
        changes = BytesIO()
        write_tree_diff(changes, self.repo.object_store, old_sha_tree,
                        new_sha_tree)
        return changes.getvalue()

    # get*
    def getLastTree(self):
        """
        return the last tree
        """
        return self.repo.get_object(self.repo.head()).tree

    def getAllTrees(self):
        """
        return trees
        """
        commit = self.repo.head()
        result = [self.repo.get_object(commit).tree]
        for c in self.repo.get_parents(commit):
            result.append(self.repo.get_object(c).tree)
        return result

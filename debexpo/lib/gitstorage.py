# -*- coding: utf-8 -*-
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2012 Baptiste Mouterde <baptiste.mouterde@gmail.com>
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

__author__ = 'Baptiste Mouterde'
__license__ = 'MIT'

from dulwich.objects import Tree, Commit, parse_timezone
from dulwich.repo import Repo
from dulwich.patch import write_tree_diff
from time import time
from io import BytesIO
import logging
import os
import pylons

log = logging.getLogger(__name__)

fileToIgnore = []


class NoOlderContent(Exception):
    pass


class GitStorage():
    def _ignoreFile(self, dirName, fileName):
        """
        used for the copTree stuff
        ``dirName``
            the working directory
        ``fileName``
            list of files inside the directory (dirName)
        """
        result = []
        for i in fileName:
            path = dirName + i
            if path not in fileToIgnore:
                result.append(path)
        return result

    def _commit(self, tree):
        """
        commit a tree used only by the init
        ``tree``
            tree to commit
        """
        commit = Commit()
        commit.tree = tree.id
        commit.encoding = "UTF-8"
        commit.committer = commit.author = ('debexpo <%s>' %
                                            (pylons.config['debexpo.email']))
        commit.commit_time = commit.author_time = int(time())
        tz = parse_timezone('-0200')[0]
        commit.commit_timezone = commit.author_timezone = tz
        commit.message = " "
        self.repo.object_store.add_object(tree)
        self.repo.object_store.add_object(commit)
        self.repo.refs["HEAD"] = commit.id
        log.debug('commiting')
        return commit.id

    def __init__(self, path):
        # Creating the repository
        if os.path.isdir(path):
            log.debug("directory exist, taking it as a git repository")
            self.repo = Repo(path)
        else:
            log.debug("directory doesn't exist, creating")
            os.makedirs(path)
            log.debug("initiate the repo")
            self.repo = Repo.init(path)
            log.debug("adding an empty tree to the repository")
            self._commit(Tree())

    # Only this function will be used on upload
    def change(self, files):
        """
        used to change a file in the git storage can be called for the first
        upload we don't care

        ``files``
            a list of file to change
        """
        if len(files) == 0:
            log.debug("trying to change nothing will do... nothing")
        else:
            log.debug("this will change %i files" % (len(files)))
            for f in files:
                self.repo.stage(f)
            log.debug("stages dones")
            self.repo.do_commit("this is so awesome that nobody will never see "
                                "it", committer="same here <foo@foo.foo>")

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

    def getOlderFileContent(self, filename):
        """
        return the first filename's content that changed from the filename
        ``filename``
            the filename to work on
        """
        # Get a list of Tree (from the newest to the oldest)
        # and skip the current one
        last_tree_with_changes = None
        history = self.getAllTrees()
        history.pop(0)

        # Find the first Tree that contains our file
        for sha in history:
            tree = self.repo.get_object(sha)
            if filename in tree:
                last_tree_with_changes = tree
                break

        # File has no previous history or does not exist in the repo
        if not last_tree_with_changes:
            raise NoOlderContent("{} has no previous version".format(filename))

        # Get corresponding blob and return its content
        (_, sha) = last_tree_with_changes[filename]
        blob = self.repo.get_object(sha)
        return blob.as_raw_string()

    def getOlderCommits(self):
        """
        return a list of all commits
        """
        return self.repo.get_parents(self.repo.head())

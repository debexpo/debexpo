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

from debexpo.lib.base import request
from dulwich.objects import Blob, Tree, Commit, parse_timezone
from dulwich.repo import Repo
from time import time
import logging
import os
import pylons
import shutil

log = logging.getLogger(__name__)

fileToIgnore = []

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
        commit.committer = commit.author = 'debexpo <%s>' % (pylons.config['debexpo.email'])
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
        #creating the repository
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

    #only this function will be used on upload
    def change(self, files):
        """
        used to change a file in the git storage can be called for the first upload we don't care
        ``files``
            a list of file to change
        """
        if len(files) == 0:
            log.debug("trying to change nothing will do... nothing")
        else:
            log.debug("this will change %i files" % (len(files)))
            for f in files:
                self.repo.stage(str(f))
            log.debug("stages dones")
            self.repo.do_commit("this is so awesome that nobody will never see it",
                committer="same here <foo@foo.foo>")

    def buildTreeDiff(self, dest, tree=None, originalTree=None):
        """
        creating files from the diff between 2 trees, it will be used in the
        code browser to get older version (walking on history)

        ``tree``
            the tree that you want to compare to
        ``dest``
            the destination folder to build sources
        ``originalTree``
            the original Tree, by default it's the last one

        by default it returns last changed files
        """
        if tree is None:
            head = self.repo.commit(self.repo.commit(self.repo.head()).parents[0])
            tree = self.repo.tree(head.tree)
        if originalTree is None:
            originalTree = self.repo.tree(self.repo.commit(self.repo.head()).tree)
        blobToBuild = []
        #getting blob that have changed
        for blob in self.repo.object_store.iter_tree_contents(tree.id):
            if blob not in originalTree:
                blobToBuild.append(blob)
                fileToIgnore.append(blob.path)
        repoLocation = os.path.join(str(self.repo).split("'")[1])
        #creating the folder with link to older files
        if os.path.exists(repoLocation + dest):
            log.warning("%s already exist, copy will not work")
        else:
            log.debug("copying files")
            shutil.copytree(repoLocation, repoLocation + dest, symlinks=True, ignore=self._ignoreFile)
        for b in blobToBuild:
            fileDirectory = os.path.split(b.path)
            fileDirectory.pop()
            if not os.path.exists(os.path.join(repoLocation + dest, os.path.join(fileDirectory))):
                os.makedirs(os.path.join(repoLocation + dest, os.path.join(fileDirectory)))
            file = open(os.path.join(repoLocation + dest, b.path), 'w')
            file.write(self.repo.get_object(b.sha).as_raw_string())
            file.close()
        tree = None
        originalTree = None

    #get*
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
        result = [ self.repo.get_object(commit).tree ]
        for c in self.repo.get_parents(commit):
            result.append(self.repo.get_object(c).tree)
        return result

    def getOlderFileContent(self, file):
        """
        return the first file's content that changed from the file
        ``file``
            the file to work on
        """
        with open(file) as f:
            originalBlob = Blob.from_string("".join(f.readlines()))
        trees = self.getAllTrees()
        for t in trees:
            #parsing tree in order to find the tree where the file change
            if originalBlob not in t:
                tree = t
                break
                #tree must be existent, other way file is not correct
        if tree is None:
            log.error(
                "there is no tree that contain this blob this souldn't happen, other way this file does not appear to come from this package")
        else:
            if self.repo._commit(self.repo.head()).tree == tree:
                olderTree = self.repo.commit(self.repo.head())._get_parents()[0].tree
            else:
                for c in self.repo._commit(self.repo.head())._get_parents():
                    if c.tree == tree:
                        try:
                            olderTree = c.get_parents()[0]
                        except IndexError:
                            log.debug("file is the last version")
                            olderTree = tree
            if olderTree != tree:
                #we must check here the blob that contains the older file
                for b in self.repo.object_store.iter_tree_contents(olderTree.id):
                    if originalBlob.path == b.path:
                        #older blob find! awesome, in the first loop we already test if they are the same
                        # that's why we can now return the content of the file
                        return self.repo.get_object(b.sha).as_raw_string()
        return ""

    def getOlderCommits(self):
        """
        return a list of all commits
        """
        return self.repo.get_parents(self.repo.head())

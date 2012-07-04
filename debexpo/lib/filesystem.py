# -*- coding: utf-8 -*-
#
#   checkfiles.py — checkfiles plugin
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#             © 2011 Arno Töll <debian@toell.net>
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
Holds various filesystem checks and interaction methods to store source package on the disk.
"""

__author__ = 'Jonny Lamb and Arno Töll'
__copyright__ = 'Copyright © 2008 Jonny Lamb, © 2011 Arno Töll'
__license__ = 'MIT'

import logging
import os
import pylons

from debexpo.lib import constants
from debexpo.lib.utils import md5sum

from debian import deb822

log = logging.getLogger(__name__)

class CheckFiles(object):

    def test_files_present(self, changes_file):
        """
        Check whether each file listed in the changes file is present.

        ```changes_file```
            The changes file to parse for the orig.tar (note the dsc file referenced must exist)
        """
        for filename in changes_file.get_files():
            log.debug('Looking whether %s was actually uploaded' % filename)
            if os.path.isfile(os.path.join(pylons.config['debexpo.upload.incoming'], filename)):
                log.debug('%s is present' % filename)
            else:
                log.critical('%s is not present; importing cannot continue' % filename)
                raise OSError("Missing file %s in incoming" % (filename))

        return True

    def test_md5sum(self, changes_file):
        """
        Check each file's md5sum and make sure the md5sum in the changes file is the same
        as the actual file's md5sum.

        ```changes_file```
            The changes file to parse for the orig.tar (note the dsc file referenced must exist)
        """
        for file in changes_file['Files']:
            log.debug('Checking md5sum of %s' % file['name'])
            filename = os.path.join(pylons.config['debexpo.upload.incoming'], file['name'])
            if not os.path.isfile(filename):
                raise OSError("Missing file %s in incoming" % (file['name']))
            sum = md5sum(filename)

            if sum != file['md5sum']:
                log.critical('%s != %s' % (sum, file['md5sum']))
                raise OSError("MD5 sum mismatch in file %s: %s != %s" % (file['name'], sum, file['md5sum']))

        return True

    def is_native_package(self, changes_file):
        """
        Guess based on the changes file and files being uploaded, whether a package
        is considered native of not

        ```changes_file```
            The changes file to parse for the orig.tar (note the dsc file referenced must exist)
        """

        for file in changes_file['Files']:
            if file['name'].endswith('.diff.gz'):
                return False
            if file['name'].endswith(('.debian.tar.gz','.debian.tar.bz2','.debian.tar.xz')):
                return False
        return True

    def find_orig_tarball(self, changes_file):
        """
        Look to see whether there is an orig tarball present, if the dsc refers to one.
        This method returns a triple (filename, file_found, location_hint), returning the (expected)
        name of the original tarball, and whether it was found in the local repository

        ```changes_file```
            The changes file to parse for the orig.tar (note the dsc file referenced must exist)

        Returns a tuple (orig_filename, orig_filename_was_found)
        """

        orig_name = None
        if not changes_file.get_dsc() or open(changes_file.get_dsc()) == None:
            return (orig_name, constants.ORIG_TARBALL_LOCATION_NOT_FOUND)

        dscfile = open(changes_file.get_dsc())
        dsc = deb822.Dsc(dscfile)
        for file in dsc['Files']:
            if (file['name'].endswith('orig.tar.gz') or
                file['name'].endswith('orig.tar.bz2') or
                file['name'].endswith('orig.tar.xz')):
                    # We know how the orig.tar.gz should be called - at least.
                    orig_name = file['name']
                    full_filename = os.path.join(pylons.config['debexpo.repository'], changes_file.get_pool_path(), orig_name)
                    # tar.gz was found in the local directory
                    if os.path.isfile(file['name']):
                        sum = md5sum(file['name'])
                        if sum == file['md5sum']:
                            return (orig_name, constants.ORIG_TARBALL_LOCATION_LOCAL)
                        # tar.gz was found, but does not seem to be the same file
                    # tar.gz was found in the repository
                    elif os.path.isfile(full_filename):
                        return (orig_name, constants.ORIG_TARBALL_LOCATION_REPOSITORY)
                    # tar.gz was expected but not found at all
                    else:
                        return (orig_name, constants.ORIG_TARBALL_LOCATION_NOT_FOUND)

        # We should neve end up here
        return (orig_name, constants.ORIG_TARBALL_LOCATION_NOT_FOUND)


    def find_files_for_packageversion(self, packageversion, absolute_path=False):
        """
        Returns all unique paths for files associated with the supplied
        package version

        ```packageversion``` The package version to be scanned

        ```absolute_path``` if set to True, returns the absolute path
            instead of a path relative to the repository root
        """
        package_files = []
        for attr in ('binary_packages', 'source_packages'):
            if hasattr(packageversion, attr):
                for bp in getattr(packageversion, attr):
                    for files in bp.package_files:
                        if not files.filename in package_files:
                            package_files.append(files.filename if not absolute_path
                                                 else pylons.config['debexpo.repository'] + files.filename)
        return package_files

    def find_files_for_package(self, package, absolute_path=False):
        """
        Returns all unique paths for files associated with the supplied
        packages

        ```package``` The package to be scanned

        ```absolute_path``` if set to True, returns the absolute path
            instead of a path relative to the repository root
        """
        package_files = []
        for p in package.package_versions:
            package_files.extend(self.find_files_for_packageversion(p, absolute_path))
        return package_files



    def delete_files_for_packageversion(self, packageversion):
        """
        Removes all files associated with the package version supplied

        ```packageversion``` PackageVersion object whose files are supposed to be removed
        """
        files = self.find_files_for_packageversion(packageversion, absolute_path=True)
        if not files:
            return
        path = os.path.dirname(files[0])
        for file in files:
            if os.path.exists(file):
                    log.debug("Removing file '%s'" % (file))
                    os.unlink(file)
        if os.path.isdir(path) and os.listdir(path) == []:
            log.debug("Remove empty package repository '%s'" % (path))
            os.rmdir(path)


    def delete_files_for_package(self, package):
        """
        Removes all files associated with the package supplied

        ```package``` package object whose files are supposed to be removed
        """
        files = self.find_files_for_package(package, absolute_path=True)
        if not files:
            return
        path = os.path.dirname(files[0])
        for file in files:
            if os.path.exists(file):
                    log.debug("Removing file '%s'" % (file))
                    os.unlink(file)
        if os.path.isdir(path) and os.listdir(path) == []:
            log.debug("Remove empty package repository '%s'" % (path))
            os.rmdir(path)





    def allowed_upload(self, filename):
        """
        Looks at a filename's extension and decides whether to accept it.
        We only want package files to be uploaded, after all.
        It returns a boolean of whether to accept the file or not.

        ``filename``
            File to test.
        """
        for suffix in ['.changes', '.dsc', '.tar.gz', '.diff.gz', '.deb', '.udeb', '.tar.bz2', ".tar.xz"]:
            if filename.endswith(suffix):
                return True

        return False


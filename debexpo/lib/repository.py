# -*- coding: utf-8 -*-
#
#   repository.py — Class to handle the repository
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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
This module holds the Repository class to handle the repository.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import bz2
import gzip
from debian import deb822, debfile
import logging
import os
from sqlalchemy import select

from debexpo.lib.utils import get_package_dir


from debexpo.model import meta
from debexpo.model.packages import Package
from debexpo.model.package_files import PackageFile
from debexpo.model.source_packages import SourcePackage
from debexpo.model.binary_packages import BinaryPackage
from debexpo.model.package_versions import PackageVersion

log = logging.getLogger(__name__)

class Repository(object):
    """
    Class to handle the repository.
    """
    def __init__(self, repository):
        """
        Class constructor. Sets the repository base directory variable and other misc variables.
        """
        self.repository = repository
        self.compression = [(gzip.GzipFile, 'gz'), (bz2.BZ2File, 'bz2')]

    def _dsc_to_sources(self, package_file):
        """
        Reads the contents of a dsc file and converts it to a Sources file entry.

        ``file``
            Filename of the dsc to read.
        """
        filename = os.path.join(self.repository, package_file.filename)
        package_version = package_file.source_package.package_version
        package = package_version.package

        if not os.path.isfile(filename):
            log.critical('Cannot find file %s' % filename)
            return ''

        if not package:
            log.critical('For some reason package is None... %s' % package_version)
            return ''

        # Read the dsc file.
        dsc = deb822.Dsc(file(filename))

        # There are a few differences between a dsc file and a Sources entry, listed and acted
        # upon below:

        # Firstly, the "Source" field in the dsc is simply renamed to "Package".
        dsc['Package'] = dsc.pop('Source')

        # There needs to be a "Directory" field to tell the package manager where to download the
        # package from. This is in the format (for the test package in the component "main"):
        #   pool/main/t/test
        dsc['Directory'] = str('pool/%s/%s' % (package_version.component, get_package_dir(package.name)))

        # The dsc file, its size, and its md5sum needs to be added to the "Files" field. This is
        # unsurprisingly not in the original dsc file!
        dsc['Files'].append({'md5sum' : package_file.md5sum, 'size': str(package_file.size), 'name' : str(package_file.filename.split('/')[-1])})

        # Get a nice rfc822 output of this dsc, now Sources, entry.
        return dsc.dump()

    def _deb_to_packages(self, package_file):
        """
        Reads a binary package and outputs a Packages file entry.

        ``file``
            Filename of the deb to read.
        """
        filename = os.path.join(self.repository, package_file.filename)
        package_version = package_file.binary_package.package_version
        package = package_version.package

        if not os.path.isfile(filename):
            log.critical('Cannot find file %s' % filename)
            return ''

        # Read the deb file.
        deb = debfile.DebFile(filename).debcontrol()

        # There are a few additions to a debian/control file to make a Packages entry, listed
        # and acted upon below:

        # (the control dictionary cannot handle Unicode - convert it)
        deb['Filename'] = str(package_file.filename)
        deb['Size'] = str(package_file.size)
        deb['MD5sum'] = str(package_file.md5sum)

        return deb.dump()

    def get_sources_file(self, distribution, component, user_id=None):
        """
        Does a query to find all packages that fit the criteria of distribution
        and component and returns the contents of a Sources file.

        ``distribution``
            Name of the distribution to look at.

        ``component``
            Name of the component to look at.

        ``user_id``
            Only look at a certain user's packages.
        """
        log.debug('Getting all sources files for dist = %s, component = %s' %
            (distribution, component))

        # Get all PackageFile instances...
        dscfiles = meta.session.query(PackageFile)

        # ...include only *.dsc files...
        dscfiles = dscfiles.filter(PackageFile.filename.like('%.dsc'))

        # ...where there is a SourcePackage instance...
        dscfiles = dscfiles.filter(PackageFile.source_package_id == SourcePackage.id)

        # ...where there is a PackageVersion instance...
        dscfiles = dscfiles.filter(SourcePackage.package_version_id == PackageVersion.id)

        # ...include only packages in the specified component...
        dscfiles = dscfiles.filter(PackageVersion.component == component)

        # ...include only package in the specified distribution...
        dscfiles = dscfiles.filter(PackageVersion.distribution == distribution)

        if user_id is not None:
            # ...where there is a Package instance...
            dscfiles = dscfiles.filter(PackageVersion.package_id == Package.id)

            # ...include only packages from this user
            dscfiles = dscfiles.filter(Package.user_id == user_id)

        # ...and finally create a list of PackageFile instances.
        dscfiles = dscfiles.all()

        entries = []

        # Loop through dsc files.
        for file in dscfiles:
            packages_entry = self._dsc_to(file)
            if not packages_entry.strip():
                log.warn('Eek, broken packages entry: %s', file)
                continue
            entries.append(packages_entry)

        # Each entry is simply joined by a blank newline, so do just that to create
        # the finished Sources file.
        return '\n'.join(entries)

    def get_packages_file(self, distribution, component, arch, user_id=None):
        """
        Does a query to find all packages that fit the criteria of distribution,
        component and architecture and returns the contents of a Packages file.

        ``distribution``
            Name of the distribution to look at.

        ``component``
            Name of the component to look at.

        ``arch``
            Name of the architecture to look at.

        ``user_id``
            Only look at a certain user's packages.
        """
        log.debug('Getting all package files for dist = %s, component = %s, arch = %s' %
            (distribution, component, arch))

        # Get all PackageFile instances...
        debfiles = meta.session.query(PackageFile)

        # ...include only *.deb files...
        debfiles = debfiles.filter(PackageFile.filename.like('%.deb'))

        # ...where there is a BinaryPackage instance...
        debfiles = debfiles.filter(PackageFile.binary_package_id == BinaryPackage.id)

        # ...where the BinaryPackage has Arch: %(arch)s or Arch: all...
        debfiles = debfiles.filter(BinaryPackage.arch == arch or BinaryPackage.arch == 'all')

        # ...where there is a PackageVersion instance...
        debfiles = debfiles.filter(BinaryPackage.package_version_id == PackageVersion.id)

        # ...include only packages in the specified component...
        debfiles = debfiles.filter(PackageVersion.component == component)

        # ...include only package in the specified distribution...
        debfiles = debfiles.filter(PackageVersion.distribution == distribution)

        if user_id is not None:
            # ...where there is a Package instance...
            debfiles = debfiles.filter(PackageVersion.package_id == Package.id)

            # ...include only packages from this user
            debfiles = debfiles.filter(Package.user_id == user_id)

        # ...and finally create a list of PackageFile instances.
        debfiles = debfiles.all()

        entries = []

        # Loop through deb files.
        for file in debfiles:
            packages_entry = self._deb_to_packages(file)
            if not packages_entry.strip():
                log.warn('Eek, broken packages entry: %s', file)
                continue
            entries.append(packages_entry)

        # Each entry is simply joined by a blank newline, so do just that to create
        # the finished Packages file.
        return '\n'.join(entries)

    def _get_archs_list(self, list):
        """
        Takes a list of directory names and returns an altered list where only items
        with "binary-" prefix stay. This "binary-" prefix is also removed.

        For example, an input of ['binary-i386', 'binary-amd64', 'foo'] would produce
        an output of ['i386', 'amd64'].

        ``list``
            List of directory names to look at.
        """
        for item in list:
            if not item.startswith('binary-'):
                list.remove(item)

        return [z[7:] for z in list]

    def _append_current_distributions(self, distributions):
        """
        Take a look at the current directory layout and add distribution - component
        entries to the ``distributions`` dict. This is useful as if the contents of the
        Sources file is empty then the file is deleted. If a package has no longer present
        but still exists in the current Sources file, this process will remove it.
        """
        distsdir = os.path.join(self.repository, 'dists')

        # The first time the repository dists files are generated, the dists directory
        # isn't present.
        if not os.path.isdir(distsdir):
            return distributions

        dists = os.listdir(distsdir)

        # Components are subdirectories in distribution directories.
        for dist in dists:
            components = os.listdir(os.path.join(distsdir, dist))

            comps = {}

            # Loop through each component.
            for component in components:
                # Get arch list.
                archs = self._get_archs_list(os.listdir(os.path.join(distsdir, dist, component)))

                if dist in distributions.keys():
                    # The distribution already exists in the big dictionary. Therefore we need to
                    # look at each component to see whether it already exists.

                    if component in distributions[dist].keys():
                        # The component already exists in the big dictionary under the current
                        # distribution. Therefore we need to look at each arch to see whether it
                        # already exists.

                        for arch in archs:
                            if arch not in distributions[dist][component]:
                                # The arch doesn't already exist. Add it.
                                distributions[dist][component].append(arch)
                    else:
                        # The component doesn't already exist. It can easily be added now then.
                        distributions[dist][component] = archs
                else:
                    # The distribution doesn't already exist in the big dictionary. Therefore
                    # we can use the temporary comps dictionary to store { component : [archs] }
                    # information.
                    comps[component] = archs

            # Test whether the comps dictionary has been used. It will only have been used when
            # the distribution didn't already exist in the big dictionary.
            if len(comps) != 0:
                distributions[dist] = comps

        return distributions

    def _get_dists_comps_archs(self):
        """
        Return a dictionary of distribution, components and dists in the distribution::

            { distribution1 : { component1 : [ arch1, arch2, ... ],
                                component2 : [ arch3, ... ] },
                                ...
              distribution2 : ...
            }

        I'm not particularly happy with the implementation of this. Perhaps one day when I'm
        much more skilled at SQLAlchemy, I'll take a look at this and see if I can perform
        all the operations on the db level. That would be nice.
        """
        log.debug('Creating dists -> components -> archs dictionary')

        # Get distinct distributions from package_versions.
        dists = meta.engine.execute(select([PackageVersion.distribution]).distinct())

        distributions = {}

        # Loop through each distribution.
        for dist in dists.fetchall():
            distributions[dist[0]] = {}

            components = meta.engine.execute(select([PackageVersion.component], PackageVersion.distribution == dist[0]).distinct())

            comps = {}

            # Loop through each component within the current distribution.
            for comp in components.fetchall():

                comps[comp[0]] = []

                # Get all distinct archs...
                archs_query = select([BinaryPackage.arch]).distinct()

                # ...where an PackageVersion instance exists for it...
                archs_query = archs_query.where(BinaryPackage.package_version_id == PackageVersion.id)

                # ...where its distribution is the current one in iteration...
                archs_query = archs_query.where(PackageVersion.distribution == dist[0])

                # ...where its component is the current one in iteration...
                archs_query = archs_query.where(PackageVersion.component == comp[0])

                # ...execute that.
                archs = meta.engine.execute(archs_query)

                # Loop through each arch.
                for arch in archs.fetchall():
                    comps[comp[0]].append(arch[0])

            # Add distribution to dictionary.
            distributions[dist[0]] = comps

        return self._append_current_distributions(distributions)

    def _check_directories(self, dist, component, arch=None):
        """
        Checks whether the directories needed for a dists file are present, and if not
        it creates them.

        ``dist``
            Name of the distribution.

        ``component``
            Name of the component within the distribution.

        ``arch``
            Architecture of the dists file. This defaults to *source*.
        """
        dir = self.repository

        # Default to source, otherwise binary-%(arch)s.
        if arch is None:
            arch = 'source'
        else:
            arch = 'binary-%s' % arch

        # Check each subdirectory of the dists directory.
        for dirname in ['dists', dist, component, arch]:
            dir = os.path.join(dir, dirname)

            if not os.path.isdir(dir):
                log.debug('Creating directory %s' % dir)
                os.mkdir(dir)

    def update_sources(self):
        """
        Updates all the Sources.{gz,bz2} files for all distributions and components
        by looking at all source packages.
        """
        log.debug('Updating Sources files')

        # Get distributions and components.
        dists = self._get_dists_comps_archs()

        for dist, components in dists.iteritems():
            for component in components.keys():
                # Make sure all directories are present.
                self._check_directories(dist, component)

                # Create Sources file content.
                sources = self.get_sources_file(dist, component)
                filename = os.path.join(self.repository, 'dists', dist, component, 'source', 'Sources')

                # If the Sources file is empty, remove Sources.{gz,bz2} files. This way the
                # directory will be removed on a clean-up as it is empty.
                if sources == '':
                    for format, extension in self.compression:
                        if os.path.isfile('%s.%s' % (filename, extension)):
                            log.debug('Removing empty Sources file: %s' % filename)
                            os.remove('%s.%s' % (filename, extension))
                else:
                    for format, extension in self.compression:
                        # Create the Sources files.
                        log.debug('Creating Sources file: %s' % filename)
                        f = format('%s.%s' % (filename, extension), 'w')
                        if type(sources) != str:
                            sources = sources.encode('utf-8')
                        f.write(sources)
                        f.close()

    def update_packages(self):
        """
        Updates all the Packages.{gz,bz2} files for all distributions and components
        by looking at all binary packages.
        """
        log.debug('Updating Packages files')

        # Get distributions and components.
        dists = self._get_dists_comps_archs()

        for dist, components in dists.iteritems():
            for component, archs in components.iteritems():
                for arch in archs:
                    # Make sure all directories are present.
                    self._check_directories(dist, component, arch)

                    # Create Packages file content.
                    packages = self.get_packages_file(dist, component, arch)
                    filename = os.path.join(self.repository, 'dists', dist, component, 'binary-%s' % arch, 'Packages')

                    # If the Packages file is empty, remove Packages.{gz,bz2} files. This way
                    # the directory will be removed on a clean-up as it is empty.
                    if packages == '':
                        for format, extension in self.compression:
                            if os.path.isfile('%s.%s' % (filename, extension)):
                                log.debug('Removing empty Packages file: %s' % filename)
                                os.remove('%s.%s' % (filename, extension))
                    else:
                        for format, extension in self.compression:
                            # Create the Packages files.
                            log.debug('Creating Packages file: %s' % filename)
                            if type(packages) == unicode:
                                packages = packages.encode('utf-8')
                            f = format('%s.%s' % (filename, extension), 'w')
                            f.write(packages)
                            f.close()

    def update(self):
        """
        Updates both Sources and Packages files in the repository.
        """
        self.update_sources()
        self.update_packages()

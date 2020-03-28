#   repository.py — Class to handle the repository
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
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

import lzma
import gzip
import logging
from tempfile import NamedTemporaryFile
from shutil import copy
from os.path import join, isfile, isdir, abspath
from os import chmod, replace, makedirs, unlink

from django.db import transaction, models
from django.utils.translation import gettext_lazy as _

from debexpo.tools.debian.dsc import Dsc
from debexpo.tools.cache import enforce_unique_instance

log = logging.getLogger(__name__)


class RepositoryFileManager(models.Manager):
    def create_from_file(self, sumed_file, basedir, changes):
        repository_file = RepositoryFile()
        repository_file.path = join(basedir, str(sumed_file))
        repository_file.size = sumed_file.size
        repository_file.sha256sum = sumed_file.checksums['sha256']
        repository_file.package = changes.source
        repository_file.version = changes.version
        repository_file.component = changes.component
        repository_file.distribution = changes.distribution

        return repository_file


# This class represents the state of the repository. Is it purposfully not
# linked to packages objects as removal can be done asynchronously (ie. when
# db package entry might already be gone).
class RepositoryFile(models.Model):
    package = models.CharField(max_length=100, verbose_name=_('Name'))
    version = models.CharField(max_length=100, verbose_name=_('Version'))
    component = models.CharField(max_length=32, verbose_name=_('Component'))
    distribution = models.CharField(max_length=32,
                                    verbose_name=_('Distribution'))

    path = models.TextField(verbose_name=_('Path'), unique=True)
    size = models.IntegerField(verbose_name=_('Size'))
    sha256sum = models.CharField(max_length=64, verbose_name=_('SHA256'))

    objects = RepositoryFileManager()

    def __str__(self):
        return self.path


class Repository():
    """
    Class to handle the repository.
    """
    def __init__(self, repository):
        """
        Class constructor. Sets the repository base directory variable and other
        misc variables.
        """
        self.repository = repository
        self.compression = [(gzip.GzipFile, 'gz'), (lzma.LZMAFile, 'xz')]
        self.pending = set()

    def __str__(self):
        return abspath(self.repository)

    def _dsc_to_sources(self, repository_file):
        """
        Reads the contents of a dsc file and converts it to a Sources file
        entry.

        ``file``
            Filename of the dsc to read.
        """
        filename = join(self.repository, repository_file.path)
        package = repository_file.package

        if not isfile(filename):
            log.critical(f'Cannot find file {filename}')
            return ''

        # Read the dsc file and get the deb822 form.
        dsc = Dsc(filename)
        source = dsc._data

        # There are a few differences between a dsc file and a Sources entry,
        # listed and acted upon below:

        # Firstly, the "Source" field in the dsc is simply renamed to "Package".
        source['Package'] = source.pop('Source')

        # There needs to be a "Directory" field to tell the package manager
        # where to download the package from. This is in the format (for the
        # test package in the component "main"):
        #   pool/main/t/test
        source['Directory'] = self._get_package_dir(
            package, repository_file.component)

        # The source file, its size, and its sha256sum needs to be added to the
        # "Checksums-Sha256" field. This is unsurprisingly not in the original
        # source file!
        source['Checksums-Sha256'].append({
            'sha256': repository_file.sha256sum,
            'size': str(repository_file.size),
            'name': repository_file.path.split('/')[-1]
        })

        # Files and Checksums-Sha1 are deprecated. Removing them from the Source
        source.pop('Files')
        source.pop('Checksums-Sha1')

        # Get a nice rfc822 output of this source, now Sources, entry.
        return source.dump()

    def get_sources_file(self, distribution, component):
        """
        Does a query to find all packages that fit the criteria of distribution
        and component and returns the contents of a Sources file.

        ``distribution``
            Name of the distribution to look at.

        ``component``
            Name of the component to look at.
        """
        # Get all RepositoryFile instances...
        dscfiles = RepositoryFile.objects \
            .filter(distribution=distribution) \
            .filter(component=component) \
            .filter(path__endswith='.dsc') \
            .all()

        entries = []

        # Loop through dsc files.
        for dsc in dscfiles:
            packages_entry = self._dsc_to_sources(dsc)
            if not packages_entry.strip():
                log.warn('Eek, broken packages entry: %s', dsc)
                continue
            entries.append(packages_entry)

        # Each entry is simply joined by a blank newline, so do just that to
        # create the finished Sources file.
        return '\n'.join(entries)

    def _check_directories(self, dist, component):
        """
        Checks whether the directories needed for a dists file are present, and
        if not it creates them.

        ``dist``
            Name of the distribution.

        ``component``
            Name of the component within the distribution.
        """
        path = join(self.repository, 'dists', dist, component, 'source')

        if not isdir(path):
            makedirs(path)

    def update_sources(self, dist, component):
        """
        Updates all the Sources.{gz,xz} files for a given distribution and
        component by looking at all source packages.
        """
        log.debug(f'Updating Sources files for {dist}/{component}')

        # Make sure all directories are present.
        self._check_directories(dist, component)

        # Create Sources file content.
        sources = self.get_sources_file(dist, component)
        dirname = join(self.repository, 'dists', dist, component, 'source')
        filename = join(dirname, 'Sources')

        for compress, extension in self.compression:
            # Create the Sources files.
            with NamedTemporaryFile(prefix='Sources', dir=dirname,
                                    delete=False) as tempfile:
                with compress(tempfile.name, 'w') as f:
                    f.write(sources.encode())
                    chmod(tempfile.name, 0o644)
                    replace(tempfile.name, f'{filename}.{extension}')

    def update(self):
        """
        Updates Sources files in the repository for dist/component that have
        been changed.
        """
        with enforce_unique_instance('repository', blocking=True):
            for dist, component in self.pending:
                self.update_sources(dist, component)

    def _get_package_dir(self, package, component):
        """
        Returns the directory name where the package with name supplied as the
        first argument should be installed.

        ``source``
            Source package name to use to work out directory name.
        """
        subpool = None

        if package.startswith('lib'):
            subpool = package[:4]
        else:
            subpool = package[0]

        return join('pool', component, subpool, package)

    def _cleanup_previous_entries(self, files_to_install, pool_dir):
        for sumed_file in files_to_install:
            # Remove old entry from database
            try:
                previous_entry = RepositoryFile.objects.get(path=join(
                    pool_dir, str(sumed_file)))
            except RepositoryFile.DoesNotExist:
                pass
            else:
                self.remove(previous_entry.package, previous_entry.version)

    def _install_new_entries(self, files_to_install, pool_dir, changes):
        dest_dir = join(self.repository, pool_dir)

        for sumed_file in files_to_install:
            if not isdir(dest_dir):
                makedirs(dest_dir)

            copy(sumed_file.filename, dest_dir)
            # And create a new one
            entry = RepositoryFile.objects.create_from_file(sumed_file,
                                                            pool_dir,
                                                            changes)
            entry.full_clean()
            entry.save()

    @transaction.atomic
    def install(self, changes):
        pool_dir = self._get_package_dir(changes.source, changes.component)
        dsc = changes.dsc
        files_to_install = [changes.files.dsc] + dsc.files.files

        self._cleanup_previous_entries(files_to_install, pool_dir)
        self._install_new_entries(files_to_install, pool_dir, changes)
        self.pending.add((changes.distribution, changes.component,))

    @transaction.atomic
    def remove(self, package, version=None):
        repository_files = RepositoryFile.objects \
            .filter(package=package)

        if version:
            repository_files = repository_files.filter(version=version)

        for repository_file in repository_files:
            path = join(self.repository, repository_file.path)
            if isfile(path):
                unlink(path)
                self.pending.add((repository_file.distribution,
                                  repository_file.component,))

        repository_files.delete()

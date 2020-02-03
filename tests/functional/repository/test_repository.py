#   test_repository.py - functional tests for repository
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from tempfile import TemporaryDirectory
from os.path import join, abspath, dirname, isfile
from os import replace, unlink
from shutil import copytree
from logging import getLogger
from gzip import GzipFile
from bz2 import BZ2File
from debian.debian_support import PackageFile

from django.urls import reverse

from debexpo.repository.models import Repository, RepositoryFile
from debexpo.tools.debian.changes import Changes

from tests import TestController
from tests.functional.importer.source_package import TestSourcePackage

log = getLogger(__name__)


class TestRepositoryController(TestController):
    def setUp(self):
        self.package = {
            'name': 'hello',
            'version': '1.0-1',
            'component': 'main',
            'distribution': 'unstable',
        }
        self.repo_dir = TemporaryDirectory()
        self.repository = Repository(self.repo_dir.name)

    def tearDown(self):
        sources = self._parse_sources()

        for source in sources:
            empty = True

            for package in source:
                empty = False

            if empty:
                unlink(source.name)

        self._assert_no_leftover(str(self.repository))

    def _repo_remove_package(self, name, version, component, distribution):
        self.repository.remove(name, version)
        self.repository.update()

    def _repo_install_package(self, name, version, component, distribution):
        # Duplicate hello sources
        source_dir = TemporaryDirectory()
        copytree(join(abspath(dirname(__file__)), '..', 'importer', 'sources',
                      'hello'), join(source_dir.name, 'sources'))

        # Templatize with name, version, component and distribution
        for filename in ('control', 'changelog',):
            old_file = join(source_dir.name, 'sources', 'debian', filename)
            with open(f'{old_file}.new', 'w') as new_file:
                with open(old_file) as fh:
                    for line in fh:
                        new_file.write(
                            line.replace('hello', name).
                            replace('1.0-1', version).
                            replace('unstable', distribution).
                            replace('Section: ', f'Section: {component}/')
                        )
            replace(f'{old_file}.new', old_file)

        # Build the new source package
        source_package = TestSourcePackage('sources', source_dir.name)
        source_package.build()

        # Install in the repository
        changes = Changes(self._find_all('.changes',
                                         source_package.get_package_dir())[0])

        changes.parse_dsc()
        self.repository.install(changes)
        self.repository.update()

    def _parse_sources(self):
        source_files = self._find_all('', join(str(self.repository), 'dists'))

        sources = []
        for source_file in source_files:
            if source_file.endswith('.gz'):
                fh = GzipFile(source_file)
            else:
                fh = BZ2File(source_file)
            sources.append(PackageFile(source_file, fh))

        return sources

    def _assert_package_in_repo(self, packages):
        db_entires = RepositoryFile.objects.all()
        pool_files = self._find_all('', join(str(self.repository), 'pool'))
        sources = self._parse_sources()

        # Assert DB entries
        packages_in_db = set()
        for entry in db_entires:
            entry_package = {
                'name': entry.package,
                'version': entry.version,
                'component': entry.component,
                'distribution': entry.distribution,
            }

            self.assertIn(entry_package, packages)
            packages_in_db.add(packages.index(entry_package))

        self.assertEquals(len(packages_in_db), len(packages))

        # Assert pool files
        for entry in db_entires:
            self.assertIn(join(str(self.repository), entry.path), pool_files)

        self.assertEquals(len(db_entires), len(pool_files))

        # Assert Sources entries
        packages_in_sources = set()
        for source in sources:

            for entry in source:
                entry_package = {
                    'name': list(filter(
                        lambda x: x[0] == "Package", entry))[0][1],
                    'version': list(filter(
                        lambda x: x[0] == "Version", entry))[0][1],
                    'component': source.name.split('/')[-3],
                    'distribution': source.name.split('/')[-4],
                }

                self.assertIn(entry_package, packages)
                packages_in_sources.add(packages.index(entry_package))

        self.assertEquals(len(packages_in_sources), len(packages))

    def test_repository_install_package(self):
        package = self.package.copy()

        # First time import
        self._repo_install_package(**package)
        self._assert_package_in_repo([package])

        # Second upload
        self._repo_install_package(**package)
        self._assert_package_in_repo([package])

        # Change the debian revision
        package['version'] = '1.0-2'
        self._repo_install_package(**package)
        self._assert_package_in_repo([package])

        # Change of distribution
        package['distribution'] = 'UNRELEASED'
        self._repo_install_package(**package)
        self._assert_package_in_repo([package])

        # Upload another package
        another = self.package.copy()
        another['name'] = 'libhello'
        self._repo_install_package(**another)
        self._assert_package_in_repo([package, another])

        # Remove first package
        self._repo_remove_package(**package)
        self._assert_package_in_repo([another])

        # Remove last package
        self._repo_remove_package(**another)

    def test_inconsistent_repository(self):
        self._repo_install_package(**self.package)
        dsc = self._find_all('.dsc', str(self.repository))[0]

        if isfile(dsc):
            unlink(dsc)

        self.repository.pending.add(('unstable', 'main'))
        self.repository.update()

        self._repo_remove_package(**self.package)

    def test_dsc_link(self):
        package = self.package
        package['name'] = 'testpackage'

        self._setup_example_user()
        self._setup_example_package()
        self._repo_install_package(**self.package)

        response = self.client.get(reverse('package', args=[package['name']]))
        self.assertEquals(response.status_code, 200)
        self.assertIn('/debian/pool/main/t/testpackage/testpackage_1.0-1.dsc',
                      str(response.content))

        self._remove_example_package()
        self._remove_example_user()
        self._repo_remove_package(**package)

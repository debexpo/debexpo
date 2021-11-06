#   origin.py - origin tarball for packages
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2011 Arno Töll <debian@toell.net>
#   Copyright © 2019-2020 Baptiste Beauplat <lyknode@cilg.org>
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

from os.path import isfile, join
from logging import getLogger

from django.conf import settings

import debexpo.repository.models as repository
from debexpo.tools.clients import ExceptionClient
from debexpo.tools.clients.ftp_master import ClientFTPMasterAPI
from debexpo.tools.clients.debian_archive import ClientDebianArchive

log = getLogger(__name__)


class ExceptionOrigin(Exception):
    pass


class Origin():
    def __init__(self, package, version, component, dest_dir):
        self.package = package
        self.version = version
        self.component = component
        self.dest_dir = dest_dir
        self.is_new = False

    def fetch(self, origin_files):
        repo = repository.Repository(settings.REPOSITORY)
        archive = ClientDebianArchive()

        # For the origin tarball and its signature
        for origin in origin_files:
            if isfile(join(self.dest_dir, str(origin))):
                # Origin file is present in the upload
                continue

            if repo.fetch_from_pool(self.package,
                                    self.component,
                                    str(origin),
                                    self.dest_dir):
                # Origin fetched from the local repository
                continue

            if not self.is_new:
                # If the package is already in Debian, retrieve it from the
                # official archive
                archive.fetch_from_pool(self.package,
                                        self.component,
                                        str(origin),
                                        self.dest_dir)

    def validate(self, source_origin_files):
        client = ClientFTPMasterAPI()
        archive_origin_files = []

        try:
            archive_origin_files = client.get_origin_files(self.package,
                                                           self.version)
        except ExceptionClient as e:
            log.warning(f'Failed to retrive origin info: {e}')

        if archive_origin_files:
            for source_file in source_origin_files:
                self._assert_same_file(source_file, archive_origin_files)
        else:
            self.is_new = True

    def _assert_same_file(self, source_file, archive_origin_files):
        for archive_file in archive_origin_files:
            if str(archive_file) == str(source_file) and \
                    archive_file != source_file:
                raise ExceptionOrigin(
                    'Source package origin file differs from '
                    'the official archive:\n\n'
                    f'Origin file         : {str(source_file)}\n\n'
                    f'sha256sum in upload : {source_file.checksums["sha256"]}\n'
                    f'sha256sum in archive: {archive_file.checksums["sha256"]}')

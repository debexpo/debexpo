#   ftp_master.py - Client for ftp-master API
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

from debian.deb822 import Deb822, Changes

from django.conf import settings

from debexpo.tools.files import CheckSumedFile
from debexpo.tools.clients import ClientJsonAPI, ClientHTTP
import debexpo.repository.models as repository


class ClientFTPMasterAPI(ClientJsonAPI):
    def get_origin_files(self, name, version):
        api = settings.FTP_MASTER_API_URL
        pool = repository.Repository.get_pool(name)
        route = f'{api}/file_in_archive/{pool}/{name}' \
                f'/{name}_{version}%25.orig%25.tar%25'
        origin_files = []

        content = self.fetch_json_resource(route)

        for match in content:
            if 'filename' in match and 'sha256sum' in match:
                origin = CheckSumedFile(match['filename'])
                origin.add_checksum('sha256', match['sha256sum'])

                origin_files.append(origin)

        return origin_files


class ClientFTPMaster(ClientHTTP):
    def get_packages_uploaded_to_new(self):
        packages = []
        content = self.fetch_resource(settings.FTP_MASTER_NEW_PACKAGES_URL)

        for package in Deb822.iter_paragraphs(content):
            packages.append(Changes(package))

        return packages

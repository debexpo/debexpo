#   debian_archive.py - Debian archive client
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste Beauplat <lyknode@cilg.org>
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

from os.path import join

from django.conf import settings

import debexpo.repository.models as repository
from debexpo.tools.clients import ClientHTTP, ExceptionClientSize, \
    ExceptionClient


class ClientDebianArchive(ClientHTTP):
    def fetch_from_pool(self, package, component, filename, dest_dir):
        pool = repository.Repository.get_pool(package)
        url = f'{settings.DEBIAN_ARCHIVE_URL}/pool/{component}/{pool}/' \
              f'{package}/{filename}'

        try:
            self.download_to_file(url, join(dest_dir, filename))
        except ExceptionClientSize:
            raise ExceptionClient(
                'The original tarball cannot be retrieved '
                'from Debian: file too big '
                f'(> {int(settings.LIMIT_SIZE_DOWNLOAD / 1024 / 1024)}MB)\n'
                'Please re-upload your package to mentors '
                'including the orig tarball.\nYou can use '
                '`dpkg-buildpackage -sa` or the appropriate flag for the\n'
                'building tool you are using.')

# -*- coding: utf-8 -*-
#
#   py.template - template for new .py files
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2019 Baptiste BEAUPLAT'
__license__ = 'MIT'

import json
import logging
import pylons

from apt_pkg import upstream_version
from os import rename
from os.path import basename, join
from tempfile import NamedTemporaryFile
from urllib import urlopen
from debexpo.lib.dsc import Dsc

log = logging.getLogger(__name__)

# Limit download size to 100 MB
LIMIT_SIZE_DOWNLOAD = 100 * 1024 * 1024


class OverSized(Exception):

    def __init__(self, limit, size):
        self.limit = limit
        self.size = size


class OfficialPackage:
    """
    This class represents an source package uploaded to the official archive
    """
    api = 'https://api.ftp-master.debian.org'

    def _fetch_resource(self, url):
        try:
            request = urlopen(url)
        except IOError as e:
            log.error('Failed to connect to debian mirror: {}\n'
                      'Url was: {}'.format(e, url))
            return None

        code = request.getcode()
        if code and code != 200:
            log.debug('Failed to get resource {}, code: {}'.format(url, code))
            return None

        size = int(request.info().get('Content-Length'))
        if size > LIMIT_SIZE_DOWNLOAD:
            raise OverSized(LIMIT_SIZE_DOWNLOAD, size)

        try:
            content = request.read()
        except IOError as e:
            log.error('Failed to connect to debian mirror: {}\n'
                      'Url was: {}'.format(e, url))
            return None

        return content

    def _get_pool(self):
        if self.name.startswith('lib'):
            pool = self.name[:4]
        else:
            pool = self.name[:1]
        return pool

    def _find_orig_in_archive(self):
        if self.uploaded_dsc.orig:
            route = '{api}/{route}/{pool}/{name}/{orig}'.format(
                        api=self.api,
                        route='file_in_archive',
                        pool=self._get_pool(),
                        name=self.name,
                        orig=self.uploaded_dsc.orig.get('name'))

            self._lookup_archive(route)
            self._lookup_archive('{}.asc'.format(route))

    def _lookup_archive(self, route):
        log.debug('Looking for {} in the official archive.'.format(route))
        content = self._fetch_resource(route)
        if content is None:
            return False

        try:
            matches = json.loads(content)
        except ValueError:
            log.error('Failed to decode reply from dak api.\nRoute was {}.'
                      'Reply was {}'.format(route, content))
            return False

        for match in matches:
            if 'filename' in match:
                log.debug('Found a match: {}'.format(match['filename']))

                if match['filename'].endswith('.asc'):
                    self.orig_asc = match
                    return True
                else:
                    self.orig = match
                    return True

        return False

    def _download_from_archive(self, orig):
        orig_url = '{mirror}/{pool}/{component}/{filename}'.format(
                        mirror=self.mirror,
                        pool='pool',
                        component=orig.get('component'),
                        filename=orig.get('filename'))
        filename = None

        log.debug('Downloading from official archive: {}'.format(orig_url))
        with NamedTemporaryFile(dir=self.queue, prefix='official_package_',
                                delete=False) as tempfile:
            content = self._fetch_resource(orig_url)

            if content is None:
                return None

            tempfile.write(content)
            filename = tempfile.name

        if filename:
            dest_filename = join(self.queue, basename(orig.get('filename')))
            rename(filename, dest_filename)
            return dest_filename

        return None

    def __init__(self, uploaded_dsc):
        self.mirror = pylons.config['debexpo.debian_mirror']
        self.queue = pylons.config['debexpo.upload.incoming']
        self.uploaded_dsc = Dsc(uploaded_dsc)
        self.name = self.uploaded_dsc.name
        self.version = upstream_version(self.uploaded_dsc.version)
        self.orig_asc = None
        self.orig = None

        log.debug('Official package info for {}-{}'.format(self.name,
                                                           self.version))
        self._find_orig_in_archive()

    def exists(self):
        return self.orig is not None

    def use_same_orig(self):
        orig = self.uploaded_dsc.orig
        orig_asc = self.uploaded_dsc.orig_asc

        if self.orig is not None and orig is None:
            return (False, 'Dsc does not reference an orig tarball'
                           ' while being present in the official archive')

        if orig is not None and self.orig is None:
            return (False, 'Dsc references an orig tarball'
                           ' while not being present in the official archive')

        if (self.orig is not None and
                self.orig.get('sha256sum') != orig.get('sha256')):
            return (False, 'Orig tarball used in the Dsc does not match orig'
                           ' present in the archive: {} != {}'.format(
                               self.orig.get('sha256sum'),
                               orig.get('sha256')))

        if self.orig_asc is not None and orig_asc is None:
            return (False, 'Dsc does not reference an orig tarball signature'
                           ' while being present in the official archive')

        if orig_asc is not None and self.orig_asc is None:
            return (False, 'Dsc references an orig tarball signature'
                           ' while not being present in the official archive')

        if (self.orig_asc is not None and
                self.orig_asc.get('sha256sum') != orig_asc.get('sha256')):
            return (False, 'Orig tarball signature used in the Dsc does not'
                           ' match orig signature present in the archive:'
                           ' {} != {}'.format(self.orig.get('sha256sum'),
                                              orig.get('sha256')))

        return (True, 'Package use same orig')

    def download_orig(self):
        downloaded = []

        for orig in (self.orig, self.orig_asc):
            if orig:
                filename = self._download_from_archive(orig)

                if not filename:
                    return None

                downloaded.append(filename)

        return downloaded

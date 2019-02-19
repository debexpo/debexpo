# -*- coding: utf-8 -*-
#
#   getorigtarball.py — getorigtarball plugin
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2011 Arno Töll <debian@toell.net>
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
Holds the getorigtarball plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, ' \
                'Copyright © 2010 Jan Dittberner, ' \
                'Copyright © 2011 Arno Töll'
__license__ = 'MIT'

import logging
import pylons

from debexpo.lib import constants
from debexpo.lib.dsc import Dsc
from debexpo.lib.filesystem import CheckFiles
from debexpo.lib.official_package import OfficialPackage, OverSized
from debexpo.lib.utils import sha256sum
from debexpo.plugins import BasePlugin
from debian import deb822
from os.path import join, isfile
from shutil import copy

log = logging.getLogger(__name__)


class GetOrigTarballPlugin(BasePlugin):

    def _validate_orig(self, dsc):
        upload = Dsc(dsc)
        orig = upload.get_dsc_item(Dsc.extract_orig)
        orig_asc = upload.get_dsc_item(Dsc.extract_orig_asc)

        files = (dsc_file for dsc_file in (orig, orig_asc) if dsc_file)
        for dsc_file in files:
            if not isfile(join(self.queue, dsc_file.get('name'))):
                return ('{} dsc reference {}, but the file was not found.\n'
                        'Please, include it in your upload.'.format(
                            dsc['Source'], dsc_file.get('name')))

            checksum = sha256sum(join(self.queue, dsc_file.get('name')))
            if dsc_file.get('sha256') != checksum:
                return ('{} dsc reference {}, but the file differs:\n'
                        'in dsc: {}\n'
                        'found: {}\n'
                        'Please, rebuild your package against the correct'
                        ' file.'.format(dsc['Source'], dsc_file.get('name'),
                                        dsc_file.get('sha256'), checksum))

    def _get_from_local_repo(self, orig_file):
        repo = pylons.config['debexpo.repository']
        filename = join(repo, self.changes.get_pool_path(), orig_file)
        upstream_sig = '{}.asc'.format(filename)

        log.debug('Orig found in local repo. '
                  'Copying to {}/{}'.format(self.queue, filename))
        copy(filename, self.queue)

        if isfile(upstream_sig):
            log.debug('Orig signature found in local repo. '
                      'Copying to {}/{}'.format(self.queue, upstream_sig))
            copy(upstream_sig, self.queue)

    def test_orig_tarball(self):
        """
        Check whether there is an original tarball referenced by the dsc file,
        but not actually in the package upload.

        This procedure is skipped to avoid denial of service attacks when a
        package is larger than the configured size
        """

        dsc = deb822.Dsc(file(self.changes.get_dsc()))
        official_package = OfficialPackage(dsc['Source'], dsc['Version'])
        self.queue = pylons.config['debexpo.upload.incoming']
        (orig_file, orig_found) = CheckFiles().find_orig_tarball(self.changes)

        if orig_found == constants.ORIG_TARBALL_LOCATION_REPOSITORY:
            # Found tarball in local repository, copying to current directory
            self._get_from_local_repo(orig_file)

        elif official_package.exists():
            # Check that we use the same orig as debian's one
            (matched, reason) = official_package.use_same_orig(dsc)
            if not matched:
                log.debug('{}'.format(reason))
                return self.failed(outcomes['mismatch-orig-debian'], reason,
                                   constants.PLUGIN_SEVERITY_ERROR)

            if orig_found == constants.ORIG_TARBALL_LOCATION_NOT_FOUND:
                # Orig was not uploaded and not found in the local repo.
                # Download it from Debian archive.
                log.debug('Downloading orig from debian archive')
                try:
                    downloaded = official_package.download_orig()
                except OverSized:
                    log.debug('Tarball to big to download')
                    return self.failed(outcomes['tarball-from-debian-too-big'],
                                       None, constants.PLUGIN_SEVERITY_ERROR)

                if not downloaded:
                    log.debug('Failed to download from debian archive')
                    return self.failed('failed-to-download', None,
                                       constants.PLUGIN_SEVERITY_ERROR)

        # Wherever the orig was retrived from, validate it against the uploaded
        # dsc.
        result = self._validate_orig(dsc)

        if result:
            return self.failed(outcomes['invalid-orig'], result,
                               constants.PLUGIN_SEVERITY_ERROR)
        else:
            return self.info(outcomes['valid-orig'], None)


plugin = GetOrigTarballPlugin

outcomes = {
    'tarball-taken-from-debian': {'name': 'The original tarball has been'
                                          ' retrieved from Debian'},
    'tarball-from-debian-too-big': {'name': 'The original tarball cannot be'
                                            ' retrieved from Debian: file too'
                                            ' big (> 100MB)'},
    'mismatch-orig-debian': {'name': 'Package was not built with orig.tar.gz'
                                     'file present in the official archives'},
    'found-in-local-repo': {'name': 'Package orig is already on mentors'},
    'found-in-upload': {'name': 'Origin tarball was uploaded with the package'},
    'invalid-orig': {'name': 'Could not find a valid orig tarball'},
    'valid-orig': {'name': 'Valid origin tarball'},
}

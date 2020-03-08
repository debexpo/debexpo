#   source_package.py — Build a source package for testing
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

import logging
from debian.debian_support import BaseVersion

from os import environ, remove
from os.path import isdir, join, dirname
from shutil import rmtree, copytree
from subprocess import Popen, PIPE, STDOUT
from tempfile import mkdtemp
from debexpo.tools.debian.changes import Changes

log = logging.getLogger(__name__)


class TestSourcePackageException(Exception):
    pass


class TestSourcePackage():
    """
    Build source packages

    From a source package:
        - creates orig tarball
        - build package
        - generate .changes
        - sign files with testing key
    """

    _GPG_KEY = """-----BEGIN PGP PRIVATE KEY BLOCK-----

lFgEW/GBqhYJKwYBBAHaRw8BAQdA+6hBA4PcdcPwgMsKGQXrqwbJemLBgS1PkKZg
RFlKdKgAAQD2uvclOFTAon1t+Auuy2cW3uc3Qf6l9ZYYskx3xYMwrBG6tCBwcmlt
YXJ5IGlkIDxwcmltYXJ5QGV4YW1wbGUub3JnPoiTBBMWCAA7AhsDBQsJCAcCBhUK
CQgLAgQWAgMBAh4BAheAFiEEVZMG7uHIwbLdHHOxxDR4HOhx898FAlvxgewCGQEA
CgkQxDR4HOhx89+RDgD/ZVwW/JZu9sT3jHY0S/k1PNz4pg9DWbq0H55y1WTruLQB
AKna8/9quNZknJyiRQJ0OaWp+RWJVJw0dlladZIhaD8LtB1UZXN0IHVzZXIgPGVt
YWlsQGV4YW1wbGUuY29tPoiQBBMWCAA4FiEEVZMG7uHIwbLdHHOxxDR4HOhx898F
AlvxgegCGwMFCwkIBwIGFQoJCAsCBBYCAwECHgECF4AACgkQxDR4HOhx898q+gD/
TMjGs/nbDgt0f1p4xPBHTONpqX91ZCmNInEutCvwI90A/15CAKrPiLUAFKHqmTN4
4dB7y8FBEsZuhbQpbcMhpasFnF0EW/GBqhIKKwYBBAGXVQEFAQEHQDa5N6qv3j9U
xFnxWaoUdL3M+2AfXOfjp7zFfsTuFt50AwEIBwAA/3JjB8KfQJ5PCuMtztVeIKdP
9BTK+pcHY6BKw5vy6DvgEaSIeAQYFggAIBYhBFWTBu7hyMGy3RxzscQ0eBzocfPf
BQJb8YGqAhsMAAoJEMQ0eBzocfPf8IcA/RyHF6zgRu2Ds3wH8GgxjCZRW+YxWahX
55/++pi9+bqyAQDp8rMxJeWXDntQn3RSfKfE7AnWF4Sd+aA+S6LPuMUICg==
=zFbo
-----END PGP PRIVATE KEY BLOCK-----"""

    def __init__(self, source_dir, data_dir=None):
        if data_dir:
            self.data_dir = data_dir
        else:
            self.data_dir = join(dirname(__file__), 'sources')

        self.source_dir = join(self.data_dir, source_dir)
        self.package = self._parse_changelog('Source').decode()
        self.version = self._parse_changelog('Version').decode()
        self.workdir = mkdtemp(prefix='debexpo-source-package')
        self.gpgdir = mkdtemp(prefix='debexpo-source-package-gpg')
        self._import_testing_key()

    def __del__(self):
        for dirs in (self.workdir, self.gpgdir):
            if isdir(dirs):
                rmtree(dirs)

    def _run_command(self, command, args, workdir, env=environ):
        proc = Popen([command] + args,
                     stdout=PIPE,
                     stderr=STDOUT,
                     cwd=join(workdir),
                     env=env)
        (output, _) = proc.communicate()

        if proc.returncode != 0:
            raise TestSourcePackageException('command failed:\n'
                                             'command: {}\n'
                                             'args: {}\n'
                                             'workdir: {}\n\n'
                                             'output: {}'.format(command, args,
                                                                 workdir,
                                                                 output))

        return output.strip()

    def _parse_changelog(self, field):
        args = ['-S', field]
        command = 'dpkg-parsechangelog'

        return self._run_command(command, args, self.source_dir)

    def _get_env_with_gpg(self):
        env = environ.copy()
        env['GNUPGHOME'] = self.gpgdir

        return env

    def _import_testing_key(self):
        args = ['--import',
                join(dirname(__file__), '..', '..', 'keyring', 'secret.gpg')]
        command = '/usr/bin/gpg'

        self._run_command(command, args, self.source_dir,
                          self._get_env_with_gpg())

    def _build_package(self):
        args = ['--build=source',
                '--no-check-builddeps',
                '--sign-key=559306EEE1C8C1B2DD1C73B1C434781CE871F3DF',
                '--force-sign']
        command = 'dpkg-buildpackage'

        log.debug('Build source package {}-{}'.format(self.package,
                                                      self.version))
        self._run_command(command, args, join(self.workdir, 'sources'),
                          self._get_env_with_gpg())

    def _gen_orig(self):
        tarball = self._get_orig_filename()
        args = ['--create',
                '--exclude=./debian',
                '--xz',
                '--file',
                tarball,
                '--directory=' + join(self.workdir, 'sources'),
                '.']
        command = 'tar'

        log.debug('Gen orig tarball {}'.format(join(self.workdir, tarball)))
        self._run_command(command, args, self.workdir)

    def _get_orig_filename(self):
        version = BaseVersion(self.version)

        return join(self.workdir,
                    f'{self.package}_{version.upstream_version}.orig.tar.xz')

    # Remove orig tarball when not referenced by .changes as it will not be
    # uploaded (copied) to the incoming spool.
    def _cleanup_orig(self):
        changes_filename = join(self.workdir, self.package + '_' + self.version
                                + '_source.changes')
        changes = Changes(changes_filename)

        found = False
        for referenced in changes.files.files:
            if '.orig.tar.xz' in str(referenced):
                found = True

        if not found:
            remove(self._get_orig_filename())

    def get_package_dir(self):
        return self.workdir

    def build(self):
        # Copy sources files into workdir
        copytree(self.source_dir,
                 join(self.workdir, 'sources'))

        # Gen orig, build and sign
        self._gen_orig()
        self._build_package()

        # Remove temporary source dir
        if isdir(join(self.workdir, 'sources')):
            rmtree(join(self.workdir, 'sources'))
        self._cleanup_orig()

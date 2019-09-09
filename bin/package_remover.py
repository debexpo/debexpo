#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#   debexpo_worker.py — Worker task
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

"""
Removes a package from debexpo
"""

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2019 Baptiste BEAUPLAT'
__license__ = 'MIT'


import apt_pkg
import re
import logging
import logging.config
import os
import sys
import ConfigParser
import optparse
import pylons

from paste.deploy import appconfig
from debexpo.config.environment import load_environment
from debexpo.model import meta
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion
from debexpo.lib.repository import Repository
from debexpo.lib.filesystem import CheckFiles

log = None
compare = {
    '<<': lambda x, y: apt_pkg.version_compare(x, y) < 0,
    '<=': lambda x, y: (apt_pkg.version_compare(x, y) == 0 or
                        apt_pkg.version_compare(x, y) < 0),
    '=': lambda x, y: apt_pkg.version_compare(x, y) == 0,
    '>=': lambda x, y: (apt_pkg.version_compare(x, y) == 0 or
                        apt_pkg.version_compare(x, y) > 0),
    '>>': lambda x, y: apt_pkg.version_compare(x, y) > 0,
}


class PackageRemover():
    def _setup(self):
        self._read_config()
        self._setup_logging()
        self._load_pylons_app()

    def _read_config(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    def _setup_logging(self):
        global log

        if not self.config.has_section('loggers'):
            print('Config file does not have [loggers] section')
            sys.exit(1)

        logging.config.fileConfig(self.config_file)
        log = logging.getLogger(__file__)

    def _load_pylons_app(self):
        sys.path.append(os.path.dirname(self.config_file))
        conf = appconfig('config:' + self.config_file)
        pylons.config = load_environment(conf.global_conf, conf.local_conf)

    def __init__(self, config_file, packages):
        apt_pkg.init_system()
        self.config_file = config_file
        self._setup()

        updated = 0
        for package in packages:
            match = re.search(r'^(?P<name>.*?)'
                              r'(?P<op>\<\<|\<=|\>=|=|\>\>)'
                              r'(?P<version>.*)$',
                              package)

            if match:
                updated += self._remove_package_version(match.group('name'),
                                                        match.group('op'),
                                                        match.group('version'))
            else:
                updated += self._remove_package(package)

        if updated > 0:
            self._update_repo()

    def _remove_package_version(self, name, op, version):
        packages = meta.session.query(Package)
        package = packages.filter_by(name=name).first()

        if not package:
            log.warn('Package {} not found'.format(name))
            return 0

        package_versions = meta.session.query(PackageVersion)
        package_versions = package_versions.filter_by(package=package).all()

        if not package_versions:
            log.warn('No package version found for {}'.format(name))
            return 0

        deleted = 0
        for package_version in package_versions:
            if compare[op](package_version.version, version):
                CheckFiles().delete_files_for_packageversion(package_version)
                meta.session.delete(package_version)
                deleted += 1
                log.info('Package version {} for {} '
                         'deleted'.format(package_version.version, name))

        if deleted == len(package_versions):
            self._remove_package(name)

        if deleted:
            meta.session.commit()

        return deleted > 0

    def _remove_package(self, package_name):
        packages = meta.session.query(Package)
        packages = packages.filter_by(name=package_name).all()

        if not packages:
            log.warn('Package {} not found'.format(package_name))
            return 0

        for package in packages:
            CheckFiles().delete_files_for_package(package)
            meta.session.delete(package)

        log.info('Package {} deleted'.format(package_name))
        meta.session.commit()
        return 1

    def _update_repo(self):
        log.info('Updating Sources/Packages files')
        repo = Repository(pylons.config['debexpo.repository'])
        repo.update()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ini", dest="ini",
                      help="path to application ini file", metavar="FILE")

    (options, args) = parser.parse_args()
    if not options.ini:
        parser.print_help()
        sys.exit(0)

    PackageRemover(options.ini, args)

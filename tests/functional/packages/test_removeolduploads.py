# -*- coding: utf-8 -*-
#
#   test_removeolduploads.py - Test the removeolduploads cronjob
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

from mako.lookup import TemplateLookup
from mako.template import Template
from os.path import join, dirname
from pylons.test import pylonsapp

import apt_pkg
import datetime
import email.parser
import logging
import pylons
import sqlalchemy.orm.exc as orm_exc

from debexpo.controllers.package import PackageController
from debexpo.controllers.packages import PackagesController
from debexpo.lib.email import Email
from debexpo.model.users import User
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion
from debexpo.tests.cronjobs import TestCronjob

log = logging.getLogger(__name__)


class TestCronjobRemoveOldUploads(TestCronjob):
    def setUp(self):
        self.nntp_server = pylonsapp.config['debexpo.nntp_server']
        pylonsapp.config['debexpo.nntp_server'] = None

        self._setup_plugin('removeolduploads', run_setup=False)
        self._finish_setup_plugin()
        self._create_user()
        self.state = []

    def tearDown(self):
        pylonsapp.config['debexpo.nntp_server'] = self.nntp_server
        self._remove_packages()
        self._remove_user()

    # This is needed since we do not call the plugin setup (to avoid the NNTP
    # connection)
    def _finish_setup_plugin(self):
        self.plugin.mailer = Email('upload_removed_from_expo')
        self.plugin.pkg_controller = PackageController()
        self.plugin.pkgs_controller = PackagesController()
        apt_pkg.init_system()
        self.plugin.last_cruft_run = datetime.datetime(year=1970,
                                                       month=1,
                                                       day=1)

    def _create_user(self):
        user = User(name='Test user',
                    email='test.user@example.org',
                    password='password',
                    lastlogin=datetime.datetime.now())
        self.db.add(user)
        self.db.commit()

    def _remove_user(self):
        user = self.db.query(User).one()
        self.db.delete(user)

    def _setup_packages(self, include_expired=False):
        packages = [
                # (package, version, distrib, expired),
                ('htop', '1.0.0', 'unstable', False),
                ('htop', '0.9.0', 'unstable', False),
                ('htop', '0.8.0', 'buster-backports', False),
                ('tmux', '1.0.0', 'unstable', False),
                ('tmux', '1.0.0', 'UNRELEASED', False),
                ('zsh', '1.0.0', 'unstable', False),
                ('zsh', '1.0.0', 'unstable', False),
                ('hello', '1.0.0', 'unstable', True),
                ('hello', '0.9.0', 'unstable', True),
            ]

        for (package, version, distrib, expired) in packages:
            if not expired or (expired and include_expired):
                self._create_package(package, version, distrib, expired)

            if not expired:
                self.state.append((package, version, distrib))

        self.db.commit()

    def _create_package(self, name, version_number, distrib, is_expired):
        date = datetime.datetime.now()
        user = self.db.query(User).one()

        try:
            package = self.db.query(Package).filter_by(name=name).one()
        except orm_exc.NoResultFound:
            package = Package(name=name,
                              user=user)

        if is_expired:
            date -= datetime.timedelta(days=365)

        version = PackageVersion(package=package,
                                 version=version_number,
                                 maintainer='vtime@example.org',
                                 section='main',
                                 distribution=distrib,
                                 qa_status=0,
                                 component='tools',
                                 uploaded=date)

        self.db.add(version)

    def _remove_packages(self):
        packages = self.db.query(Package)

        for package in packages:
            self.db.delete(package)

        self.db.commit()

    def _assert_cronjob_success(self):
        packages = self.db.query(Package)
        count = 0

        # Each package exists in state
        for package in packages:
            for version in package.package_versions:
                log.debug('validating {}-{}/{}'.format(package.name,
                                                       version.version,
                                                       version.distribution))
                self.assertTrue((package.name,
                                 version.version,
                                 version.distribution) in self.state)
                count += 1

        # Each state exists in package
        self.assertEquals(len(self.state), count)

    def _expect_package_removal(self, package_to_remove):
        new_state = []

        for package in self.state:
            if package not in package_to_remove:
                new_state.append(package)

        self.state = new_state

    def _build_email(self, package):
        (name, version, distrib) = package
        c = {'name': name, 'version': version, 'distrib': distrib}
        template_file = join(dirname(__file__), 'email/accept.mako')
        lookup = TemplateLookup(directories=[dirname(template_file)])
        template = Template(
            filename=template_file, lookup=lookup,
            module_directory=pylons.config['app_conf']['cache_dir'])

        return email.message_from_string(template.render_unicode(c=c))

    def _invoke_plugin(self, uploaded):
        for package in uploaded:
            message = self._build_email(package)
            self.plugin._process_changes(message)

        self.plugin._remove_old_packages()

    def test_remove_uploads_noop_no_packages(self):
        self._invoke_plugin([])
        self._assert_cronjob_success()

    def test_remove_uploads_inexistant_package(self):
        self._invoke_plugin([('inexistant_package', '1.0.0', 'unstable')])
        self._assert_cronjob_success()

    def test_remove_uploads_noop_with_packages(self):
        self._setup_packages()
        self._invoke_plugin([])
        self._assert_cronjob_success()

    def test_remove_uploads_expired(self):
        self._setup_packages(include_expired=True)
        self._invoke_plugin([])
        self._assert_cronjob_success()

    def test_remove_uploads_keep_other_dists(self):
        removed_packages = [
                ('htop', '1.0.0', 'unstable'),
                ('htop', '0.9.0', 'unstable'),
            ]

        self._setup_packages()
        self._invoke_plugin([('htop', '1.0.0', 'unstable')])
        self._expect_package_removal(removed_packages)
        self._assert_cronjob_success()

    def test_remove_uploads_same_version(self):
        removed_packages = [
                ('zsh', '1.0.0', 'unstable'),
            ]

        self._setup_packages()
        self._invoke_plugin([('zsh', '1.0.0', 'unstable')])
        self._expect_package_removal(removed_packages)
        self._assert_cronjob_success()

    def test_remove_uploads_keep_newer(self):
        removed_packages = [
                ('htop', '0.9.0', 'unstable'),
            ]

        self._setup_packages()
        self._invoke_plugin([('htop', '0.9.0', 'unstable')])
        self._expect_package_removal(removed_packages)
        self._assert_cronjob_success()

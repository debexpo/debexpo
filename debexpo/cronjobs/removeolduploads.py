# -*- coding: utf-8 -*-
#
#   removeolduploads.py -- remove old and uploaded packages from Debexpo
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
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
Import RFS comments from debian-mentors
"""
__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2011 Arno Töll'
__license__ = 'MIT'

from debexpo.cronjobs import BaseCronjob

from debexpo.lib.email import Email
from debexpo.lib.filesystem import CheckFiles
from debexpo.controllers.package import PackageController
from debexpo.controllers.packages import PackagesController
from debexpo.model.users import User
from debexpo.model.data_store import DataStore
from debexpo.model import meta
from debian import deb822

import socket
import re
import apt_pkg
import datetime

__namespace__ = '_remove_uploads_'

class RemoveOldUploads(BaseCronjob):

    def _remove_package(self, package, version, reason):
        user = meta.session.query(User).filter_by(id=package.user_id).one()
        if user:
            self.mailer.send([user.email, ],
                package=package.name,
                version=version,
                reason=reason)

        CheckFiles().delete_files_for_package(package)
        meta.session.delete(package)
        meta.session.commit()

    def _process_changes(self, mail):
        if mail.is_multipart():
            self.log.debug("Changes message is multipart?!")
            return
        changes = mail.get_payload(decode=True)
        try:
            changes = deb822.Changes(changes)
        except:
            self.log.error('Could not open changes file; skipping mail "%s"' % (mail['subject']))
            return

        if not 'Source' in changes:
            #self.log.debug('Changes file "%s" seems incomplete' % (mail['subject']))
            return
        package = self.pkg_controller._get_package(changes['Source'], from_controller=False)
        if package != None:
            for pv in package.package_versions:
                if pv.distribution == changes['Distribution'] and apt_pkg.VersionCompare(changes['Version'], pv.version) == 0:
                    self.log.debug("Package %s was was uploaded to Debian - removing it from Expo" % (changes['Source']))
                    self._remove_package(package, pv.version, "Package was uploaded to official Debian repositories")
        else:
            #self.log.debug("Package %s was not uploaded to Expo before - ignoring it" % (changes['Source']))
            pass

    def _remove_uploaded_packages(self):

        if self.mailer.connection_established():
            lists = meta.session.query(DataStore).filter(DataStore.namespace == __namespace__).all()
            for list_name in lists:
                for message in self.mailer.unread_messages(list_name.code, list_name.value):
                    self._process_changes(message)
                    list_name.value = message['X-Debexpo-Message-Number']
                self.log.debug("Processed all messages up to #%s on %s" % (list_name.value, list_name.code))
                meta.session.merge(list_name)
            meta.session.commit()
            self.mailer.disconnect_from_server()

    def _remove_old_packages(self):
        now = datetime.datetime.now()
        for package in self.pkgs_controller._get_packages():
            if (now - package.package_versions[-1].uploaded) > datetime.timedelta(weeks = 20):
                self.log.debug("Removing package %s - uploaded on %s" % (package.name, package.package_versions[-1].uploaded))
                self._remove_package(package, "all versions", "Your package found no sponsor for 20 weeks")

    def setup(self):
        self.mailer = Email('upload_removed_from_expo')
        self.mailer.connect_to_server()
        self.pkg_controller = PackageController()
        self.pkgs_controller = PackagesController()
        apt_pkg.InitSystem()
        self.last_cruft_run = datetime.datetime(year=1970, month=1, day=1)
        self.log.debug("%s loaded successfully" % (__name__))



    def teardown(self):
        self.mailer.disconnect_from_server()

    def invoke(self):
        try:
            self._remove_uploaded_packages()
        except socket.error as e:
            # better luck next time
            self.log.debug("Socket error %s: skipping removals his time" % (e))
            pass

        # We don't need to run our garbage collection of old cruft that often
        # It's ok if we purge old packages once a day.
        if (datetime.datetime.now() - self.last_cruft_run) >= datetime.timedelta(hours = 24):
            self.last_cruft_run = datetime.datetime.now()
            self._remove_old_packages()

cronjob = RemoveOldUploads
schedule = datetime.timedelta(minutes = 10)

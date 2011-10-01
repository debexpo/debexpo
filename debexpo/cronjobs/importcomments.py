# -*- coding: utf-8 -*-
#
#   importcomments.py — Import RFS comments from debian-mentors
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
from debexpo.model.users import User
from debexpo.model import meta
from debian import deb822

import re
import apt_pkg
import datatime

class ImportComments(BaseCronjob):
    def _belongs_to_package(self, mail):
        # Policy 5.6.1 defines source package names as collection of
        # lower case letters (a-z), digits (0-9), plus (+) and minus (-)
        # signs, and periods (.)
        match = re.search('(Re: |)RFS: ([a-z0-9\+\-\.]+)', mail['subject'], re.IGNORECASE)
        if (match):
            packagename = match.group(2)
            package = meta.session.query(Package).filter_by(name=packagename).first()
            #self.log.debug("'%s' => %s" % (packagename, package))
            if not package:
                return None
            return package

        return None

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
                if pv.distribution == changes['Distribution'] and apt_pkg.VersionCompare(changes['Version'], pv.version) >= 0:
                    self.log.debug("Package %s was was uploaded to Debian - removing it from Expo" % (changes['Source']))
                    user = meta.session.query(User).filter_by(id=package.user_id).one()
                    if user:
                        self.mailer.send([user.email, ],
                            package=package.name,
                            version=pv.version,
                            reason='Package was uploaded to official Debian repositories')
                    CheckFiles().delete_files_for_package(package)
                    meta.session.delete(package)
                    meta.session.commit()
                    break
        else:
            #self.log.debug("Package %s was not uploaded to Expo before - ignoring it" % (changes['Source']))
            pass

    def _process_mentors(self, mail):
        return
        if mail.is_multipart():
            self.log.debug("Mentors message is multipart?!")
            return
        package = self._belongs_to_package(mail)
        if not package:
            self.log.debug("Post '%s' on debian-mentors seems not to be related to a package I know" % (mail['subject']))
            return
        #XXX: Finish me


    def setup(self):
        self.mailer = Email('upload_removed_from_expo')
        # Set readonly=True to keep messages untouched on the server
        # This is useful to debug
        self.mailer.connect_to_server(readonly=False)
        self.pkg_controller = PackageController()
        apt_pkg.InitSystem()

    def teardown(self):
        self.mailer.disconnect_from_server()

    def invoke(self):
        filter_pattern = ('list-id',
            ['<debian-devel-changes.lists.debian.org>',
            '<debian-mentors.lists.debian.org>',
            '<debian-changes.lists.debian.org>',
            '<debian-backports-changes.lists.debian.org>']
        )

        if self.mailer.connection_established():
            for message in self.mailer.unread_messages(filter_pattern):
                if 'list-id' in message:
                    if message['list-id'] in ('<debian-devel-changes.lists.debian.org>',
                            '<debian-changes.lists.debian.org>',
                            '<debian-backports-changes.lists.debian.org>'):
                        self._process_changes(message)
                        # We can remove processes messages now. They either where not related to us
                        # or we didn't care.
                        self.mailer.remove_message(message)
                        continue
                    elif message['list-id'] == '<debian-mentors.lists.debian.org>':
                        self._process_mentors(message)
                        self.mailer.mark_as_unseen(message)
                        continue
                #self.mailer.remove_message(message)

cronjob = ImportComments
schedule = datetime.timedelta(minutes = 10)

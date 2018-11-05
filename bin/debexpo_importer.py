#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#   debexpo-importer — executable script to import new packages
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

""" Executable script to import new packages. """

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

from optparse import OptionParser
import ConfigParser
from datetime import datetime
from debian import deb822
import logging
import logging.config
import os
import re
import sys
import shutil
from stat import *
import pylons
import email.utils

from sqlalchemy import exc as exceptions

# Horrible imports
from debexpo.model import meta
import debexpo.lib.helpers as h
from debexpo.lib.utils import parse_section, md5sum
from debexpo.lib.email import Email
from debexpo.lib.plugins import Plugins
from debexpo.lib import constants
from pylons import tmpl_context as c
#from pylons import url
from routes.util import url_for as url

# Import model objects
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion
from debexpo.model.source_packages import SourcePackage
from debexpo.model.binary_packages import BinaryPackage
from debexpo.model.package_files import PackageFile
from debexpo.model.package_info import PackageInfo
from debexpo.model.package_subscriptions import PackageSubscription

# Import debexpo modules
from paste.deploy import appconfig
from debexpo.config.environment import load_environment
from debexpo.lib.email import Email
from debexpo.lib.changes import Changes
from debexpo.lib.repository import Repository
from debexpo.lib.plugins import Plugins
from debexpo.lib.filesystem import CheckFiles
from debexpo.lib.gnupg import GnuPG

log = None

class Importer(object):
    """
    Class to handle the package that is uploaded and wants to be imported into the database.
    """

    def __init__(self, changes, ini, skip_email, skip_gpg):
        """
        Object constructor. Sets class fields to sane values.

        ``self``
            Object pointer.

        ``changes``
            Name `changes` file to import. This is given from the upload controller.

        ``ini``
            Path to debexpo configuration file. This is given from the upload controller.

        ``skip_email``
            If this is set to true, send no email.
        """
        self.changes_file_unqualified = changes
        self.ini_file = os.path.abspath(ini)
        self.actually_send_email = not bool(skip_email)
        self.skip_gpg = skip_gpg

        self.user_id = None
        self.changes = None
        self.user = None

    def send_email(self, email, *args, **kwargs):
        if self.actually_send_email:
            email.send(*args, **kwargs)
        else:
            logging.info("Skipping email send: %s %s", args, kwargs)

    @property
    def changes_file(self):
        incoming_dir = pylons.config['debexpo.upload.incoming']
        return os.path.join(incoming_dir, self.changes_file_unqualified)

    def _remove_changes(self):
        """
        Removes the `changes` file.
        """
        if os.path.exists(self.changes_file):
                os.remove(self.changes_file)

    def _remove_temporary_files(self):
        if hasattr(self, 'files_to_remove'):
            for file in self.files_to_remove:
                if os.path.exists(file):
                    os.remove(file)

    def _remove_files(self):
        """
        Removes all the files uploaded.
        """
        if hasattr(self, 'files'):
            for file in self.files:
                if os.path.exists(file):
                    os.remove(file)

        self._remove_changes()
        self._remove_temporary_files()

    def _fail(self, reason, use_log=True):
        """
        Fail the upload by sending a reason for failure to the log and then remove all
        uploaded files.

        A package is `fail`ed if there is a problem with debexpo, **not** if there's
        something wrong with the package.

        ``reason``
            String of why it failed.

        ``use_log``
            Whether to use the log. This should only be False when actually loading the log fails.
            In this case, the reason is printed to stderr.
        """
        if use_log:
            log.critical(reason)
        else:
            print >> sys.stderr, reason

        self._remove_files()

        if self.user is not None:
            email = Email('importer_fail_maintainer')
            package = self.changes.get('Source', '')


            self.send_email(email, [self.user.email], package=package)

        email = Email('importer_fail_admin')
        self.send_email(email, [pylons.config['debexpo.email']], message=reason)

        sys.exit(1)

    def _reject(self, reason):
        """
        Reject the package by sending a reason for failure to the log and then remove all
        uploaded files.

        A package is `reject`ed if there is a problem with the package.

        ``reason``
            String of why it failed.
        """
        log.error('Rejected: %s' % reason)

        self._remove_changes()
        self._remove_files()

        if self.user is not None:
            email = Email('importer_reject_maintainer')
            package = self.changes.get('Source', '')

            self.send_email(email, [self.user.email], package=package, message=reason)
        sys.exit(1)

    def _setup_logging(self):
        """
        Parse the config file and create the ``log`` object for other methods to log their
        actions.
        """
        global log

        # Parse the ini file to validate it
        parser = ConfigParser.ConfigParser()
        parser.read(self.ini_file)

        # Check for the presence of [loggers] in self.ini_file
        if not parser.has_section('loggers'):
            self._fail('Config file does not have [loggers] section', use_log=False)

        logging.config.fileConfig(self.ini_file)

        # Use "name.pid" to avoid importer confusions in the logs
        logger_name = 'debexpo.importer.%s' % os.getpid()
        log = logging.getLogger(logger_name)

    def _setup(self):
        """
        Set up logging, import pylons/paste/debexpo modules, parse config file, create config
        class and chdir to the incoming directory.
        """
        # Look for ini file
        if not os.path.isfile(self.ini_file):
            self._fail('Cannot find ini file')

        self._setup_logging()

        # Import debexpo root directory
        sys.path.append(os.path.dirname(self.ini_file))

        # Initialize Pylons app
        conf = appconfig('config:' + self.ini_file)
        pylons.config = load_environment(conf.global_conf, conf.local_conf)

        # Change into the incoming directory
        incoming_dir = pylons.config['debexpo.upload.incoming']
        logging.info("Changing dir to %s", incoming_dir)
        os.chdir(incoming_dir)

        # Look for the changes file
        if not os.path.isfile(self.changes_file):
            self._fail('Cannot find changes file')

    def _create_db_entries(self, qa):
        """
        Create entries in the Database for the package upload.
        """

        def _package_description(raw):
            return raw[2:].replace('      - ', ' - ')

        log.debug('Creating database entries')


        # Parse component and section from field in changes
        component, section = parse_section(self.changes['files'][0]['section'])

        # Check whether package is already in the database
        package_query = meta.session.query(Package).filter_by(name=self.changes['Source'])
        if package_query.count() == 1:
            log.debug('Package %s already exists in the database' % self.changes['Source'])
            package = package_query.one()
            # Update description to make sure it reflects the latest upload
            package.description = _package_description(self.changes['Description'])
        else:
            log.debug('Package %s is new to the system' % self.changes['Source'])
            package = Package(name=self.changes['Source'], user=self.user)
            package.description = _package_description(self.changes['Description'])
	    package.needs_sponsor = 0
            meta.session.add(package)

        # No need to check whether there is the same source name and same version as an existing
        # entry in the database as the upload controller tested whether similar filenames existed
        # in the repository. The only way this would be wrong is if the filename had a different
        # version in than the Version field in changes..

        try:
            closes = self.changes['Closes']
        except KeyError:
            closes = None

        # TODO: fix these magic numbers
        if qa.stop():
            qa_status = 1
        else:
            qa_status = 0

        maintainer_matches = re.compile(r'(.*) <(.*)>').match(self.changes['Changed-By'])
        maintainer = maintainer_matches.group(2)

        package_version = PackageVersion(package=package, version=self.changes['Version'],
            section=section, distribution=self.changes['Distribution'], qa_status=qa_status,
            component=component, priority=self.changes.get_priority(), closes=closes,
            uploaded=datetime.now(), maintainer=maintainer)
        meta.session.add(package_version)

        source_package = SourcePackage(package_version=package_version)
        meta.session.add(source_package)

        binary_package = None

        # Add PackageFile objects to the database for each uploaded file
        for file in self.files:
            filename = os.path.join(self.changes.get_pool_path(), file)
            # This exception should be never caught.
            # It implies something went wrong before, as we expect a file which does not exist
            try:
                sum = md5sum(os.path.join(pylons.config['debexpo.repository'], filename))
            except AttributeError as e:
                self._fail("Could not calculate MD5 sum: %s" % (e))

            size = os.stat(os.path.join(pylons.config['debexpo.repository'], filename))[ST_SIZE]

            # Check for binary or source package file
            if file.endswith('.deb'):
                # Only create a BinaryPackage if there actually binary package files
                if binary_package is None:
                    binary_package = BinaryPackage(package_version=package_version, arch=file[:-4].split('_')[-1])
                    meta.session.add(binary_package)

                meta.session.add(PackageFile(filename=filename, binary_package=binary_package, size=size, md5sum=sum))
            else:
                meta.session.add(PackageFile(filename=filename, source_package=source_package, size=size, md5sum=sum))

        meta.session.commit()
        log.warning("Finished adding PackageFile objects.")

        # Add PackageInfo objects to the database for the package_version
        for result in qa.result:
            meta.session.add(PackageInfo(package_version=package_version, from_plugin=result.from_plugin,
                outcome=result.outcome, rich_data=result.data, severity=result.severity))

        # Commit all changes to the database
        meta.session.commit()
        log.debug('Committed package data to the database')

        subscribers = meta.session.query(PackageSubscription).filter_by(package=self.changes['Source']).filter(\
            PackageSubscription.level <= constants.SUBSCRIPTION_LEVEL_UPLOADS).all()

        if len(subscribers) > 0:
            email = Email('package_uploaded')
            self.send_email(email, [s.user.email for s in subscribers], package=self.changes['Source'],
                version=self.changes['Version'], user=self.user)

            log.debug('Sent out package subscription emails')

        # Send success email to uploader
        email = Email('successful_upload')
        dsc_url = pylons.config['debexpo.server'] + '/debian/' + self.changes.get_pool_path() + '/' + self.changes.get_dsc()
        rfs_url = pylons.config['debexpo.server'] + url('rfs', packagename=self.changes['Source'])
        self.send_email(email, [self.user.email], package=self.changes['Source'],
            dsc_url=dsc_url, rfs_url=rfs_url)

        return package_version


    def _determine_uploader(self):
        """
        Create a user object based on the Changed-By entry
        This object will also exist if the user was NOT found. This is useful
        to have a user object to send reject mails to
        """
        if self.user_id is None:
            maintainer_string = self.changes.get('Changed-By')
            log.debug("Determining user from 'Changed-By:' field: %s" % maintainer_string)
            maintainer_realname, maintainer_email_address = email.utils.parseaddr(maintainer_string)
            log.debug("Changed-By's email address is: %s", maintainer_email_address)
            self.user = meta.session.query(User).filter_by(
                    email=maintainer_email_address).filter_by(verification=None).first()
            if self.user is None:
                # generate user object, but only to send out reject message
                self.user = User(id=-1, name=maintainer_realname, email=maintainer_email_address)
            self.user_id = self.user.id

    def main(self):
        """
        Actually start the import of the package.

        Do several environment sanity checks, move files into the right place, and then
        create the database entries for the imported package.
        """
        # Set up importer
        self._setup()

        log.debug('Importer started with arguments: %s' % sys.argv[1:])
        filecheck = CheckFiles()
        signature = GnuPG()

        # Try parsing the changes file, but fail if there's an error.
        try:
            self.changes = Changes(filename=self.changes_file)
            filecheck.test_files_present(self.changes)
            filecheck.test_md5sum(self.changes)
        except Exception as e:
            # XXX: The user won't ever see this message. The changes file was
            # invalid, we don't know whom send it to
            self._reject("Your changes file appears invalid. Refusing your upload\n%s" % (str(e)))

        # Determine user from changed-by field
        # This might be temporary, the GPG check should replace the user later
        # At this stage it is only helpful to get an email address to send blame mails to
        self._determine_uploader()

        # Checks whether the upload has a dsc file
        if not self.changes.get_dsc():
            self._reject("Rejecting incomplete upload.\nYou did not upload the"
                         " dsc file\nMake sure you include the full source"
                         " (if you are using sbuild make sure to use the"
                         " --source option or the equivalent configuration"
                         " item; if you are using dpkg-buildpackage directly"
                         " use the default flags or -S for a source only"
                         " upload)")

        # Next, find out whether the changes file was signed with a valid signature, if not reject immediately
        if not self.skip_gpg:
            if not signature.is_signed(self.changes_file):
                self._reject('Your upload does not appear to be signed')
            (gpg_out, gpg_status) = signature.verify_sig_full(self.changes_file)
            if gpg_status != 0:
                self._reject('Your upload does not contain a valid signature. Output was:\n%s' % (gpg_out))
            log.debug("GPG signature matches user %s" % (self.user.email))

        # XXX: Replace self.user by something which was verified by GPG!

        if self.user_id == -1:
            self._reject('Couldn\'t find user %s. Exiting.' % self.user.email)
        log.debug("User found in database. Has id: %s", self.user.id)

        self.files = self.changes.get_files()
        self.files_to_remove = []

        distribution = self.changes['Distribution'].lower()
        allowed_distributions = (
            'bullseye',
            'bullseye-backports',
            'bullseye-backports-sloppy',
            'bullseye-security',
            'bullseye-updates',
            'buster',
            'buster-backports',
            'buster-backports-sloppy',
            'buster-security',
            'buster-updates',
            'experimental',
            'jessie',
            'jessie-backports',
            'jessie-backports-sloppy',
            'jessie-security',
            'jessie-updates',
            'oldstable',
            'oldstable-backports',
            'oldstable-backports-sloppy',
            'oldstable-proposed-updates',
            'oldstable-security',
            'sid',
            'squeeze',
            'squeeze-backports',
            'squeeze-backports-sloppy',
            'squeeze-security',
            'squeeze-updates',
            'stable',
            'stable-backports',
            'stable-proposed-updates',
            'stable-security',
            'stretch',
            'stretch-backports',
            'stretch-backports-sloppy',
            'stretch-security',
            'stretch-updates',
            'testing',
            'testing-proposed-updates',
            'testing-security',
            'unreleased',
            'unstable',
            'wheezy',
            'wheezy-backports',
            'wheezy-backports-sloppy',
            'wheezy-security',
            'wheezy-updates',
        )
        if distribution not in allowed_distributions:
            self._reject("You are not uploading to one of those Debian distributions: %s" %
                (reduce(lambda x,xs: x + " " + xs, allowed_distributions)))

        # Look whether the orig tarball is present, and if not, try and get it from
        # the repository.
        (orig, orig_file_found) = filecheck.find_orig_tarball(self.changes)
        if orig_file_found != constants.ORIG_TARBALL_LOCATION_LOCAL:
            log.debug("Upload does not contain orig.tar.gz - trying to find it elsewhere")
        if orig and orig_file_found == constants.ORIG_TARBALL_LOCATION_REPOSITORY:
            filename = os.path.join(pylons.config['debexpo.repository'],
                self.changes.get_pool_path(), orig)
            if os.path.isfile(filename):
                log.debug("Found tar.gz in repository as %s" % (filename))
                shutil.copy(filename, pylons.config['debexpo.upload.incoming'])
                # We need the orig.tar.gz for the import run, plugins need to extract the source package
                # also Lintian needs it. However the orig.tar.gz is in the repository already, so we can
                # remove it later
                self.files_to_remove.append(orig)

        destdir = pylons.config['debexpo.repository']


        # Check whether the files are already present
        log.debug("Checking whether files are already in the repository")
        toinstall = []
        pool_dir = os.path.join(destdir, self.changes.get_pool_path())
        log.debug("Pool directory: %s", pool_dir)
        for file in self.files:
            if os.path.isfile(file) and os.path.isfile(os.path.join(pool_dir, file)):
                log.warning('%s is being installed even though it already exists' % file)
                toinstall.append(file)
            elif os.path.isfile(file):
                log.debug('File %s is safe to install' % os.path.join(pool_dir, file))
                toinstall.append(file)
            # skip another corner case, where the dsc contains a orig.tar.gz but wasn't uploaded
            # by doing nothing here for that case

        # Run post-upload plugins.
        post_upload = Plugins('post-upload', self.changes, self.changes_file,
            user_id=self.user_id)
        if post_upload.stop():
            log.critical('post-upload plugins failed')
            self._remove_changes()
            sys.exit(1)

        # Check whether a post-upload plugin has got the orig tarball from somewhere.
        if not orig_file_found and not filecheck.is_native_package(self.changes):
            (orig, orig_file_found) = filecheck.find_orig_tarball(self.changes)
            if orig_file_found == constants.ORIG_TARBALL_LOCATION_NOT_FOUND:
                # When coming here it means:
                # a) The uploader did not include a orig.tar.gz in his upload
                # b) We couldn't find a orig.tar.gz in our repository
                # c) No plugin could get the orig.tar.gz
                # ... time to give up
                if orig == None:
                    orig = "any original tarball (orig.tar.gz)"
                self._reject("Rejecting incomplete upload. "
                    "You did not upload %s and we didn't find it on any of our alternative resources.\n" \
                    "If you tried to upload a package which only increased the Debian revision part, make sure you include the full source (pass -sa to dpkg-buildpackage)" %
                    ( orig ))
            else:
                toinstall.append(orig)

        # Check whether the debexpo.repository variable is set
        if 'debexpo.repository' not in pylons.config:
            self._fail('debexpo.repository not set')

        # Check whether debexpo.repository is a directory
        if not os.path.isdir(pylons.config['debexpo.repository']):
            self._fail('debexpo.repository is not a directory')

        # Check whether debexpo.repository is writeable
        if not os.access(pylons.config['debexpo.repository'], os.W_OK):
            self._fail('debexpo.repository is not writeable')

        qa = Plugins('qa', self.changes, self.changes_file, user_id=self.user_id)
        if qa.stop():
            self._reject('QA plugins failed the package')

        # Loop through parent directories in the target installation directory to make sure they
        # all exist. If not, create them.
        for dir in self.changes.get_pool_path().split('/'):
            destdir = os.path.join(destdir, dir)

            if not os.path.isdir(destdir):
                log.debug('Creating directory: %s' % destdir)
                os.mkdir(destdir)

        # Install files in repository
        for file in toinstall:
            log.debug("Installing new file %s" % (file))
            shutil.move(file, os.path.join(destdir, file))
            os.chmod(os.path.join(destdir, file), 0o644)

        self._remove_temporary_files()
        # Create the database rows
        package_version = self._create_db_entries(qa)

        # Execute post-successful-upload plugins
        f = open(self.changes_file)
        changes_contents = f.read()
        f.close()
        Plugins('post-successful-upload', self.changes, self.changes_file,
            changes_contents=changes_contents)

        # Remove the changes file
        self._remove_changes()

        # Refresh the Sources/Packages files.
        log.debug('Updating Sources and Packages files')
        r = Repository(pylons.config['debexpo.repository'])
        r.update()

        log.debug('Done')


def main():
    parser = OptionParser(usage="%prog -c FILE -i FILE [--skip-email] [--skip-gpg-check]")
    parser.add_option('-c', '--changes', dest='changes',
                      help='Path to changes file to import',
                      metavar='FILE', default=None)
    parser.add_option('-i', '--ini', dest='ini',
                      help='Path to application ini file',
                      metavar='FILE', default=None)
    parser.add_option('--skip-email', dest='skip_email',
                      action="store_true", help="Skip sending emails")
    parser.add_option('--skip-gpg-check', dest='skip_gpg',
                      action="store_true", help="Skip the GPG signedness check")

    (options, args) = parser.parse_args()

    if not options.changes or not options.ini:
        parser.print_help()
        sys.exit(0)

    i = Importer(options.changes, options.ini, options.skip_email, options.skip_gpg)

    i.main()
    return 0

if __name__=='__main__':
    main()

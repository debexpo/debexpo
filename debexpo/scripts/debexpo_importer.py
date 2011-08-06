# -*- coding: utf-8 -*-
#
#   debexpo-importer — executable script to import new packages
#
#   This file is part of debexpo - http://debexpo.workaround.org
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

from sqlalchemy import exceptions

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
from debexpo.lib.base import config
from debexpo.lib.email import Email
from debexpo.lib.changes import Changes
from debexpo.lib.repository import Repository
from debexpo.lib.plugins import Plugins



log = None

class Importer(object):
    """
    Class to handle the package that is uploaded and wants to be imported into the database.
    """

    def __init__(self, changes, ini, user_id):
        """
        Object constructor. Sets class fields to sane values.

        ``self``
            Object pointer.

        ``changes``
            Name `changes` file to import. This is given from the upload controller.

        ``ini``
            Path to debexpo configuration file. This is given from the upload controller.

        ``user_id``
            ID of the user doing the upload. This is given from the upload controller.
        """
        self.changes_file = os.path.abspath(changes)
        self.ini_file = os.path.abspath(ini)
        self.user_id = user_id
        self.changes = None
        self.user = None

    def _remove_changes(self):
        """
        Removes the `changes` file.
        """
        os.remove(self.changes_file)

    def _remove_files(self):
        """
        Removes all the files uploaded.
        """
        if hasattr(self, 'files'):
            for file in self.files:
                if os.path.exists(file):
                    os.remove(file)

        self._remove_changes()

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

            email.send([self.user.email], package=package)

        email = Email('importer_fail_admin')
        email.send([config['debexpo.email']], message=reason)

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

        self._remove_files()

        if self.user is not None:
            email = Email('importer_reject_maintainer')
            package = self.changes.get('Source', '')

            email.send([self.user.email], package=package, message=reason)
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
        os.chdir(pylons.config['debexpo.upload.incoming'])

        # Look for the changes file
        if not os.path.isfile(self.changes_file):
            self._fail('Cannot find changes file')

    def _create_db_entries(self, qa):
        """
        Create entries in the Database for the package upload.
        """
        log.debug('Creating database entries')

        # Parse component and section from field in changes
        component, section = parse_section(self.changes['files'][0]['section'])

        # Check whether package is already in the database
        package_query = meta.session.query(Package).filter_by(name=self.changes['Source'])
        if package_query.count() == 1:
            log.debug('Package %s already exists in the database' % self.changes['Source'])
            package = package_query.one()
        else:
            log.debug('Package %s is new to the system' % self.changes['Source'])
            package = Package(name=self.changes['Source'], user=self.user)
            package.description = self.changes['Description'][2:].replace('      - ', ' - ')
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

        maintainer_matches = re.compile(r'(.*) <(.*)>').match(self.changes['Maintainer'])
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
            sum = md5sum(os.path.join(pylons.config['debexpo.repository'], filename))
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
            log.debug("Adding result: %s", result)
            meta.session.add(PackageInfo(package_version=package_version, from_plugin=result.from_plugin,
                outcome=result.outcome, data=result.data, severity=result.severity))

        # Commit all changes to the database
        meta.session.commit()
        log.debug('Committed package data to the database')

        subscribers = meta.session.query(PackageSubscription).filter_by(package=self.changes['Source']).filter(\
            PackageSubscription.level <= constants.SUBSCRIPTION_LEVEL_UPLOADS).all()

        if len(subscribers) > 0:
            email = Email('package_uploaded')
            email.send([s.user.email for s in subscribers], package=self.changes['Source'],
                version=self.changes['Version'], user=self.user)

            log.debug('Sent out package subscription emails')

        # Send success email to uploader
        email = Email('successful_upload')
        dsc_url = pylons.config['debexpo.server'] + '/debian/' + self.changes.get_pool_path() + '/' + self.changes.get_dsc()
        rfs_url = pylons.config['debexpo.server'] + url('rfs', packagename=self.changes['Source'])
        email.send([self.user.email], package=self.changes['Source'],
            dsc_url=dsc_url, rfs_url=rfs_url)

    def _orig(self):
        """
        Look to see whether there is an orig tarball present, if the dsc refers to one.
        If it is present or not necessary, this returns True. Otherwise, it returns the
        name of the file required.
        """
        dsc = deb822.Dsc(open(self.changes.get_dsc()))
        for file in dsc['Files']:
            if (file['name'].endswith('orig.tar.gz') or
                file['name'].endswith('orig.tar.bz2')):
                if os.path.isfile(file['name']):
                    return True
                else:
                    return file['name']

        return True

    def main(self):
        """
        Actually start the import of the package.

        Do several environment sanity checks, move files into the right place, and then
        create the database entries for the imported package.
        """
        # Set up importer
        self._setup()

        log.debug('Importer started with arguments: %s' % sys.argv[1:])

        # Try parsing the changes file, but fail if there's an error.
        try:
            self.changes = Changes(filename=self.changes_file)
        except Exception, e:
            log.error(e.message)
            self._remove_changes()
            sys.exit(1)

        self.files = self.changes.get_files()

        # Look whether the orig tarball is present, and if not, try and get it from
        # the repository.
        orig = self._orig()
        if orig is not True:
            filename = os.path.join(pylons.config['debexpo.repository'],
                self.changes.get_pool_path(), orig)
            if os.path.isfile(filename):
                shutil.copy(filename, pylons.config['debexpo.upload.incoming'])
                self.files.append(orig)
            else:
                oldorig = orig
                orig = None

        destdir = pylons.config['debexpo.repository']

        # If the user ID wasn't specified using the "-u" option then try
        # to determine it from the "Maintainer:" mentioned in the changes
        # file.
        if self.user_id is None:
            log.debug("Option '-u' was not given. Determining user from 'Maintainer:' field.")
            maintainer_string = self.changes.get('Maintainer')
            log.debug("Maintainer is: %s", maintainer_string)
            maintainer_realname, maintainer_email_address = email.utils.parseaddr(maintainer_string)
            log.debug("Maintainer's email address is: %s", maintainer_email_address)
            self.user = meta.session.query(User).filter_by(
                    email=maintainer_email_address).filter_by(verification=None).first()
            if self.user is None:
                self._fail('Couldn\'t find user with email address %s. Exiting.' % self.maintainer_email_address)
            log.debug("User found in database. Has id: %s", self.user.id)
        else:
            # Get uploader's User object
            self.user = meta.session.query(User).filter_by(id=self.user_id).filter_by(verification=None).first()
            if self.user is None:
                self._fail('Couldn\'t find user with id %s. Exiting.' % self.user_id)

        # Check whether the files are already present
        log.debug("Checking whether files are already in the repository")
        toinstall = []
        pool_dir = os.path.join(destdir, self.changes.get_pool_path())
        log.debug("Pool directory: %s", pool_dir)
        for file in self.files:
            if os.path.isfile(os.path.join(pool_dir, file)):
                log.warning('%s is being installed even though it already exists' % file)
            else:
                log.debug('File %s is safe to install' % os.path.join(pool_dir, file))
                toinstall.append(file)

        # Run post-upload plugins.
        post_upload = Plugins('post-upload', self.changes, self.changes_file,
            user_id=self.user_id)
        if post_upload.stop():
            log.critical('post-upload plugins failed')
            self._remove_changes()
            sys.exit(1)

        # Check whether a post-upload plugin has got the orig tarball from somewhere.
        if orig is None:
            if self._orig():
                self.files.append(oldorig)

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
            shutil.move(file, os.path.join(destdir, file))

        # Create the database rows
        self._create_db_entries(qa)

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
    parser = OptionParser(usage="%prog [-u ID] -c FILE -i FILE")
    parser.add_option('-c', '--changes', dest='changes',
                      help='Path to changes file to import',
                      metavar='FILE', default=None)
    parser.add_option('-i', '--ini', dest='ini',
                      help='Path to application ini file',
                      metavar='FILE', default=None)
    # If the 'userid' option is not given then the user will be derived
    # from the email address mentioned in the changes file as Maintainer.
    parser.add_option('-u', '--userid', dest='user_id',
                      help='''Uploader's user_id''',
                      metavar='ID', default=None)

    (options, args) = parser.parse_args()

    if not options.changes or not options.ini:
        parser.print_help()
        sys.exit(0)

    i = Importer(options.changes, options.ini, options.user_id)

    i.main()
    return 0

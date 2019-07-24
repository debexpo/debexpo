#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#   debexpo-importer — executable script to import new packages
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
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

import ConfigParser
from datetime import datetime
from debian import deb822
from stat import ST_SIZE
import logging
import logging.config
import os
import re
import sys
import shutil
import string
import subprocess
import tempfile
import pylons
import email.utils

# Horrible imports
from debexpo.lib.utils import parse_section, md5sum, sha256sum
from debexpo.lib.dsc import Dsc
from debexpo.lib import constants
# from pylons import url
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
from debexpo.lib.gitstorage import GitStorage

log = None


class Importer(object):
    """
    Class to handle the package that is uploaded and wants to be imported into
    the database.
    """

    def __init__(self, changes, ini, skip_email, skip_gpg):
        """
        Object constructor. Sets class fields to sane values.

        ``self``
            Object pointer.

        ``changes``
            Name `changes` file to import. This is given from the upload
            controller.

        ``ini``
            Path to debexpo configuration file. This is given from the upload
            controller.

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
            log.info("Skipping email send: %s %s", args, kwargs)

    @property
    def changes_file(self):
        incoming_dir = pylons.config['debexpo.upload.incoming']
        return os.path.join(incoming_dir, self.changes_file_unqualified)

    def _clean_path(self, pathToRemove, files):
        """
        remove a path from another using magic split
        ''pathToRemove''
            the path to remove
        ''filePath''
            the a list of original filePath
        """
        result = []
        for filePath in files:
            filePath = string.split(filePath, pathToRemove)
            filePath = filePath[1]
            filePath = string.split(filePath, os.sep)
            if filePath[0] == '':
                filePath.remove('')
            fileName = string.join(filePath, os.sep)
            result.append(fileName)
        return result

    def _get_files(self, path):
        """
        return all files in a path
        ''path''
            the path we are searching
        """
        result = []
        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path, f)):
                result += self._get_files(os.path.join(path, f))
            else:
                result.append(os.path.join(path, f))
        return result

    def _extract_source(self, extract_dir):
        log.debug('Copying files to a temp directory to run dpkg-source -x on'
                  ' the dsc file')
        self.tempdir = tempfile.mkdtemp()
        log.debug('Temp dir is: %s', self.tempdir)
        for filename in self.changes.get_files():
            log.debug('Copying: %s', filename)
            shutil.copy(os.path.join(pylons.config['debexpo.upload.incoming'],
                                     filename), self.tempdir)

        # If the original tarball was pulled from Debian or from the repository,
        # that also needs to be copied into this directory.
        dsc = deb822.Dsc(file(self.changes.get_dsc()))
        for item in dsc['Files']:
            if item['name'] not in self.changes.get_files():
                src_file = os.path.join(
                    pylons.config['debexpo.upload.incoming'], item['name'])
                repository_src_file = os.path.join(
                    pylons.config['debexpo.repository'],
                    self.changes.get_pool_path(),
                    item['name'])
                if os.path.exists(src_file):
                    shutil.copy(src_file, self.tempdir)
                elif os.path.exists(repository_src_file):
                    shutil.copy(repository_src_file, self.tempdir)
                else:
                    log.critical("Trying to copy non-existing file %s" %
                                 (src_file))

        shutil.copy(os.path.join(pylons.config['debexpo.upload.incoming'],
                                 self.changes_file), self.tempdir)
        self.oldcurdir = os.path.abspath(os.path.curdir)
        os.chdir(self.tempdir)

        log.debug("Extracting sources for {}".format(dsc['Source']))
        extract = subprocess.Popen(['/usr/bin/dpkg-source',
                                    '-x',
                                    '--no-copy',
                                    self.changes.get_dsc(),
                                    extract_dir],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        (output, _) = extract.communicate()

        shutil.rmtree(self.tempdir)
        os.chdir(self.oldcurdir)

        if extract.returncode:
            log.critical("Failed to extract sources for"
                         " {}:\n{}".format(dsc['Source'], output))
            return False
        else:
            return True

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
        Fail the upload by sending a reason for failure to the log and then
        remove all uploaded files.

        A package is `fail`ed if there is a problem with debexpo, **not** if
        there's something wrong with the package.

        ``reason``
            String of why it failed.

        ``use_log``
            Whether to use the log. This should only be False when actually
            loading the log fails.  In this case, the reason is printed to
            stderr.
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

    def _reject(self, reason):
        """
        Reject the package by sending a reason for failure to the log and then
        remove all uploaded files.

        A package is `reject`ed if there is a problem with the package.

        ``reason``
            String of why it failed.
        """
        log.error('Rejected: %s' % reason)

        self._remove_files()

        if self.user is not None:
            email = Email('importer_reject_maintainer')
            package = self.changes.get('Source', '')

            self.send_email(email, [self.user.email], package=package,
                            message=reason)

    def _setup_logging(self, no_env):
        """
        Parse the config file and create the ``log`` object for other methods to
        log their actions.
        """
        global log

        if not no_env:
            # Parse the ini file to validate it
            parser = ConfigParser.ConfigParser()
            parser.read(self.ini_file)

            # Check for the presence of [loggers] in self.ini_file
            if not parser.has_section('loggers'):
                self._fail('Config file does not have [loggers] section',
                           use_log=False)
                return 1

            logging.config.fileConfig(self.ini_file)

        # Use "name.pid" to avoid importer confusions in the logs
        logger_name = 'debexpo.importer.%s' % os.getpid()
        log = logging.getLogger(logger_name)

    def _setup(self, no_env):
        """
        Set up logging, import pylons/paste/debexpo modules, parse config file,
        create config class and chdir to the incoming directory.
        """
        # Look for ini file
        if not os.path.isfile(self.ini_file):
            self._fail('Cannot find ini file')
            return 1

        self._setup_logging(no_env)

        # Import debexpo root directory
        sys.path.append(os.path.dirname(self.ini_file))

        if not no_env:
            # Initialize Pylons app
            conf = appconfig('config:' + self.ini_file)
            pylons.config = load_environment(conf.global_conf, conf.local_conf)

        # Change into the incoming directory
        incoming_dir = pylons.config['debexpo.upload.incoming']
        log.info("Changing dir to %s", incoming_dir)
        os.chdir(incoming_dir)

        # Look for the changes file
        if not os.path.isfile(self.changes_file):
            self._fail('Cannot find changes file')
            return 1

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
        package_query = meta.session.query(Package) \
            .filter_by(name=self.changes['Source'])
        if package_query.count() == 1:
            log.debug('Package %s already exists in the database' %
                      self.changes['Source'])
            package = package_query.one()
            # Update description to make sure it reflects the latest upload
            package.description = _package_description(
                self.changes.get('Description', ''))
        else:
            log.debug('Package %s is new to the system' %
                      self.changes['Source'])
            package = Package(name=self.changes['Source'], user=self.user)
            package.description = _package_description(
                    self.changes.get('Description', ''))
            package.needs_sponsor = 0
            meta.session.add(package)

        # No need to check whether there is the same source name and same
        # version as an existing entry in the database as the upload controller
        # tested whether similar filenames existed in the repository. The only
        # way this would be wrong is if the filename had a different version in
        # than the Version field in changes..

        try:
            closes = self.changes['Closes']
        except KeyError:
            closes = None

        # TODO: fix these magic numbers
        if qa.stop():
            qa_status = 1
        else:
            qa_status = 0

        maintainer_matches = re.compile(r'(.*) <(.*)>') \
            .match(self.changes['Changed-By'])
        maintainer = maintainer_matches.group(2)

        package_version = PackageVersion(
            package=package,
            version=self.changes['Version'],
            section=section,
            distribution=self.changes['Distribution'],
            qa_status=qa_status,
            component=component,
            priority=self.changes.get_priority(),
            closes=closes,
            uploaded=datetime.now(),
            maintainer=maintainer)
        meta.session.add(package_version)

        source_package = SourcePackage(package_version=package_version)
        meta.session.add(source_package)

        binary_package = None

        # Add PackageFile objects to the database for each uploaded file
        for file in self.files:
            filename = os.path.join(self.changes.get_pool_path(), file)

            # This exception should be never caught.  It implies something went
            # wrong before, as we expect a file which does not exist
            try:
                md5 = md5sum(os.path.join(
                    pylons.config['debexpo.repository'], filename))
            except AttributeError as e:
                self._fail("Could not calculate MD5 sum: %s" % (e))
                return 1

            try:
                sha256 = sha256sum(os.path.join(
                    pylons.config['debexpo.repository'], filename))
            except AttributeError as e:
                self._fail("Could not calculate SHA256 sum: %s" % (e))
                return 1

            size = os.stat(os.path.join(
                pylons.config['debexpo.repository'], filename))[ST_SIZE]

            # Clean old entries referencing the same file.
            meta.session.query(PackageFile).filter(
                    PackageFile.filename == filename
                ).delete()

            # Check for binary or source package file
            if file.endswith('.deb'):
                # Only create a BinaryPackage if there actually binary package
                # files
                if binary_package is None:
                    binary_package = BinaryPackage(
                        package_version=package_version,
                        arch=file[:-4].split('_')[-1])
                    meta.session.add(binary_package)

                meta.session.add(PackageFile(filename=filename,
                                             binary_package=binary_package,
                                             size=size, md5sum=md5,
                                             sha256sum=sha256))
            else:
                meta.session.add(PackageFile(filename=filename,
                                             source_package=source_package,
                                             size=size, md5sum=md5,
                                             sha256sum=sha256))

        meta.session.commit()
        log.warning("Finished adding PackageFile objects.")

        # Add PackageInfo objects to the database for the package_version
        for result in qa.result:
            # Catch description from controlfields plugin, add it to the package
            # and remove it from the plugin data
            if (result.from_plugin == 'controlfields' and
                    'Description' in result.data):
                package.description = result.data.get('Description', '')
                result.data.pop('Description')
                meta.session.commit()

            meta.session.add(PackageInfo(package_version=package_version,
                                         from_plugin=result.from_plugin,
                                         outcome=result.outcome,
                                         rich_data=result.data,
                                         severity=result.severity))

        # Commit all changes to the database
        meta.session.commit()
        log.debug('Committed package data to the database')

        subscribers = meta.session.query(PackageSubscription) \
            .filter_by(package=self.changes['Source']) \
            .filter(PackageSubscription.level >=
                    constants.SUBSCRIPTION_LEVEL_UPLOADS) \
            .all()

        if len(subscribers) > 0:
            email = Email('package_uploaded')
            self.send_email(email, [s.user.email for s in subscribers],
                            package=self.changes['Source'],
                            version=self.changes['Version'],
                            user=self.user)

            log.debug('Sent out package subscription emails')

        # Send success email to uploader
        email = Email('successful_upload')
        dsc_url = pylons.config['debexpo.server'] + '/debian/' + \
            self.changes.get_pool_path() + '/' + self.changes.get_dsc()
        rfs_url = pylons.config['debexpo.server'] + \
            url('rfs', packagename=self.changes['Source'])
        self.send_email(email, [self.user.email],
                        package=self.changes['Source'], dsc_url=dsc_url,
                        rfs_url=rfs_url)

        return package_version

    def _find_user_by_email_address(self, email_address):
        """
        Searches user by email address
        """
        # XXX: Maybe model is more appropriate place for such a method
        user = meta.session.query(User) \
            .filter_by(email=email_address) \
            .filter_by(verification=None) \
            .first()
        if user:
            self.user = user
        return user

    def _determine_uploader_by_changedby_field(self):
        """
        Create a user object based on the Changed-By entry
        """
        maintainer_string = self.changes.get('Changed-By')
        log.debug("Determining user from 'Changed-By:' field: %s" %
                  maintainer_string)
        maintainer_realname, maintainer_email_address = email.utils.parseaddr(
            maintainer_string)
        log.debug("Changed-By's email address is: %s", maintainer_email_address)
        if not self._find_user_by_email_address(maintainer_email_address):
            # Creates a fake user object, but only if no user was found before,
            # this is useful to have a user object to send reject mails to.
            self.user = User(id=-1, name=maintainer_realname,
                             email=maintainer_email_address)

    def _determine_uploader_by_gpg(self, gpg_out):
        """
        Create a user object based on the gpg output
        """

        for (name, mail) in gpg_out:
            log.debug("GPG signature matches user %s <%s>" % (name, mail))
            if self._find_user_by_email_address(mail):
                log.debug("GPG signature mapped to user %s <%s>" %
                          (self.user.name, self.user.email))
                return True

        return False

    def _check_changes_files(self):
        filecheck = CheckFiles()

        try:
            filecheck.test_files_present(self.changes)
            filecheck.test_md5sum(self.changes)
        except Exception as e:
            self._reject("Your upload looks incomplete or corrupt:\n\n"
                         "{}".format(str(e)))
            return False

        return True

    def _store_source_as_git_repo(self):
        # Exit now if gitstorage is not enabled
        if pylons.config['debexpo.gitstorage.enabled'] != 'true':
            return

        # Setup some variable used by git storage
        destdir = pylons.config['debexpo.repository']
        git_storage_repo = os.path.join(destdir, "git", self.changes['Source'])
        git_storage_sources = os.path.join(git_storage_repo,
                                           self.changes['Source'])

        # Initiate the git storage
        gs = GitStorage(git_storage_repo)
        if os.path.isdir(git_storage_sources):
            log.debug("git storage: remove previous sources")
            shutil.rmtree(git_storage_sources, True)

        # Building sources
        log.debug("git storage: extract sources")
        if self._extract_source(git_storage_sources):
            # Record sources
            fileToAdd = self._get_files(git_storage_sources)
            fileToAdd = self._clean_path(git_storage_repo, fileToAdd)
            gs.change(fileToAdd)

    def _validate_orig_files(self, dsc):
        upload = Dsc(deb822.Dsc(file(dsc)))
        orig = upload.orig
        orig_asc = upload.orig_asc
        queue = pylons.config['debexpo.upload.incoming']

        files = (dsc_file for dsc_file in (orig, orig_asc) if dsc_file)
        for dsc_file in files:
            filename = os.path.join(queue, dsc_file.get('name'))
            if not os.path.isfile(filename):
                self._reject('{} dsc reference {}, but the file was not found'
                             '.\nPlease, include it in your upload'
                             '.'.format(upload.name, dsc_file.get('name')))
                return False

            checksum = sha256sum(filename)
            if dsc_file.get('sha256') != checksum:
                self._reject('{} dsc reference {}, but the file differs:\n'
                             'in dsc: {}\n'
                             'found: {}\n\n'
                             'Please, rebuild your package against the correct'
                             ' file.'.format(upload.name,
                                             dsc_file.get('name'),
                                             dsc_file.get('sha256'), checksum))
                return False

        return True

    def main(self, no_env=False):
        """
        Actually start the import of the package.

        Do several environment sanity checks, move files into the right place,
        and then create the database entries for the imported package.
        """
        # Set up importer
        self._setup(no_env)

        signature = GnuPG()

        # Try parsing the changes file, but fail if there's an error.
        try:
            self.changes = Changes(filename=self.changes_file)
        except Exception as e:
            # XXX: The user won't ever see this message. The changes file was
            # invalid, we don't know whom send it to
            self._reject("Your changes file appears invalid. Refusing your "
                         "upload\n%s" % (str(e)))
            return 1

        # Determine user from changed-by field
        # This might be temporary, the GPG check should replace the user later
        # At this stage it is only helpful to get an email address to send blame
        # mails to
        self._determine_uploader_by_changedby_field()

        # Check that all files referenced in the changelog are present and match
        # their checksum
        if not self._check_changes_files():
            return 1

        # Checks whether the upload has a dsc file
        if not self.changes.get_dsc():
            self._reject("Rejecting incomplete upload.\nYou did not upload the"
                         " dsc file\nMake sure you include the full source"
                         " (if you are using sbuild make sure to use the"
                         " --source option or the equivalent configuration"
                         " item; if you are using dpkg-buildpackage directly"
                         " use the default flags or -S for a source only"
                         " upload)")
            return 1

        if not self.skip_gpg:
            # Next, find out whether the changes file was signed with a valid
            # signature, if not reject immediately
            if not signature.is_signed(self.changes_file):
                self._reject('Your upload does not appear to be signed')
                return 1
            (gpg_out, gpg_uids, gpg_status) = signature.verify_sig_full(
                self.changes_file)
            if gpg_status != 0:
                self._reject('Your upload does not contain a valid signature. '
                             'Output was:\n%s' % (gpg_out))
                return 1
            if not self._determine_uploader_by_gpg(gpg_uids):
                self._reject('Rejecting your upload. Your GPG key does not'
                             ' match the email used to register')
                return 1

        if self.user.id == -1:
            self._reject('Couldn\'t find user %s. Exiting.' % self.user.email)
            return 1

        self.user_id = self.user.id
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
            self._reject("You are not uploading to one of those Debian "
                         "distributions: %s" %
                         (reduce(lambda x, xs: x + " " + xs,
                                 allowed_distributions)))
            return 1

        # Check whether the debexpo.repository variable is set
        if 'debexpo.repository' not in pylons.config:
            self._fail('debexpo.repository not set')
            return 1

        # Check whether debexpo.repository is a directory
        if not os.path.isdir(pylons.config['debexpo.repository']):
            self._fail('debexpo.repository is not a directory')
            return 1

        # Check whether debexpo.repository is writeable
        if not os.access(pylons.config['debexpo.repository'], os.W_OK):
            self._fail('debexpo.repository is not writeable')
            return 1

        destdir = pylons.config['debexpo.repository']

        # Check whether the files are already present
        log.debug("Checking whether files are already in the repository")
        toinstall = []
        pool_dir = os.path.join(destdir, self.changes.get_pool_path())
        log.debug("Pool directory: %s", pool_dir)
        for file in self.files:
            if (os.path.isfile(file) and
                    os.path.isfile(os.path.join(pool_dir, file))):
                log.warning('%s is being installed even though it already '
                            'exists' % file)
                toinstall.append(file)
            elif os.path.isfile(file):
                log.debug('File %s is safe to install' %
                          os.path.join(pool_dir, file))
                toinstall.append(file)
                # skip another corner case, where the dsc contains a orig.tar.gz
                # but wasn't uploaded by doing nothing here for that case

        # Run post-upload plugins.
        post_upload = Plugins('post-upload', self.changes, self.changes_file,
                              user_id=self.user_id)
        if post_upload.stop():
            log.critical('post-upload plugins failed')
            self._remove_files()
            return 1

        # Get results from getorigtarball
        getorigtarball = None
        for result in post_upload.result:
            if result.from_plugin == 'getorigtarball':
                getorigtarball = result

        # If getorigtarball did not succeed, send a reject mail
        if getorigtarball:
            if getorigtarball.data:
                (details, additional_files) = getorigtarball.data
                toinstall.extend(additional_files)
                self.files_to_remove.extend(additional_files)

            if getorigtarball.severity == constants.PLUGIN_SEVERITY_ERROR:
                msg = "Rejecting your upload\n\n"
                msg += getorigtarball.outcome.get('name')
                if getorigtarball.data:
                    msg += "\n\nDetails:\n{}".format(details)
                self._reject(msg)
                return 1

        # Validates orig files from the uploaded dsc
        if not self._validate_orig_files(self.changes.get_dsc()):
            return 1

        qa = Plugins('qa', self.changes, self.changes_file,
                     user_id=self.user_id)
        if qa.stop():
            if qa.result > 0 and qa.result[0].from_plugin == "extract":
                self._reject('Fail to extract your package:'
                             '\n\n{}'.format(qa.result[0].outcome))
            else:
                self._reject('QA plugins failed the package')
            return 1

        self._store_source_as_git_repo()

        # Loop through parent directories in the target installation directory
        # to make sure they all exist. If not, create them.
        for dir in self.changes.get_pool_path().split('/'):
            destdir = os.path.join(destdir, dir)

            if not os.path.isdir(destdir):
                log.debug('Creating directory: %s' % destdir)
                os.mkdir(destdir)

        # Install files in repository
        for file in toinstall:
            filename = os.path.basename(file)
            log.debug("Installing new file {} to {}".format(
                filename, os.path.join(destdir, filename)))
            shutil.move(file, os.path.join(destdir, filename))
            os.chmod(os.path.join(destdir, filename), 0o644)

        self._remove_temporary_files()
        # Create the database rows
        self._create_db_entries(qa)

        # Execute post-successful-upload plugins
        f = open(self.changes_file)
        changes_contents = f.read()
        f.close()
        Plugins('post-successful-upload', self.changes, self.changes_file,
                changes_contents=changes_contents)

        # Remove the changes file
        self._remove_files()

        # Refresh the Sources/Packages files.
        log.debug('Updating Sources and Packages files')
        r = Repository(pylons.config['debexpo.repository'])
        r.update()

        log.debug('Done')
        return 0

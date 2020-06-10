#   models.py - importer logic
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from logging import getLogger

from os.path import join, exists, basename
from os import makedirs, unlink
from glob import glob

from django.db import transaction
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from debexpo.packages.models import Distribution, PackageUpload, \
    SourcePackage, BinaryPackage
from debexpo.accounts.models import User
from debexpo.tools.debian.changes import Changes, ExceptionChanges
from debexpo.tools.debian.dsc import ExceptionDsc
from debexpo.tools.debian.origin import ExceptionOrigin
from debexpo.tools.clients import ExceptionClient
from debexpo.tools.debian.source import Source, ExceptionSource
from debexpo.tools.debian.control import ExceptionControl
from debexpo.tools.debian.copyright import ExceptionCopyright
from debexpo.tools.debian.changelog import ExceptionChangelog
from debexpo.tools.files import ExceptionCheckSumedFile
from debexpo.tools.gnupg import ExceptionGnuPG
from debexpo.tools.email import Email
from debexpo.repository.models import Repository
from debexpo.plugins.models import PluginManager
from debexpo.tools.gitstorage import GitStorage

log = getLogger(__name__)

# Compression method supported by dpkg
DPKG_COMPRESSION_ALGO = ('bz2', 'gz', 'xz')


class ExceptionSpool(Exception):
    pass


class ExceptionSpoolUploadDenied(ExceptionSpool):
    pass


class ExceptionImporter(Exception):
    def __init__(self, changes=None, error=None, details=None):
        self.changes = changes
        self.error = error
        self.details = details

    def __str__(self):
        return f'Failed to import {self.changes.source}: {self.error}\n' \
               f'{self.details}'


class ExceptionImporterRejected(ExceptionImporter):
    pass


class Spool():
    def __init__(self, spool):
        self.spool = spool
        self.queues = {
            'incoming': join(self.spool, 'incoming'),
            'processing': join(self.spool, 'processing'),
        }

        for queue in (self.queues.values()):
            if not exists(queue):
                try:
                    makedirs(queue)
                except OSError as e:
                    raise ExceptionSpool(e)

    def upload(self, name):
        name = basename(name)

        if not self._allowed_extention(name):
            raise ExceptionSpoolUploadDenied(
                'Filetype is not allowed on this server')

        if self._is_owned(name):
            raise ExceptionSpoolUploadDenied(
                'File already queued for importation')

        return open(join(self.queues['incoming'], name), 'wb')

    def _is_owned(self, name):
        if not exists(join(self.queues['incoming'], name)):
            return False

        for changes in self.get_all_changes('incoming'):
            # Only use valid changes
            try:
                changes.validate()
                changes.authenticate()
                changes.files.validate()
            except (ExceptionChanges, ExceptionCheckSumedFile, ExceptionGnuPG):
                pass
            else:
                if changes.owns(name):
                    return True

                if str(changes) == name:
                    return True

        return False

    def _allowed_extention(self, filename):
        suffixes = [
            '.asc',
            '.buildinfo',
            '.changes',
            '.deb',
            '.diff.gz',
            '.dsc',
            '.udeb',
        ]

        for algo in DPKG_COMPRESSION_ALGO:
            suffixes.append('tar.{}'.format(algo))

        for suffix in suffixes:
            if filename.endswith(suffix):
                return True

        return False

    def get_all_changes(self, queue):
        changes = []

        for name in glob(join(self.queues[queue], '*.changes')):
            try:
                changes.append(Changes(name))
            except ExceptionChanges as e:
                log.warning(e)
                unlink(name)

        return changes

    def changes_to_process(self):
        for changes in self.get_all_changes('incoming'):
            changes.move(self.queues['processing'])

        return self.get_all_changes('processing')

    def get_queue_dir(self, queue):
        return self.queues[queue]

    def __str__(self):
        return self.spool


class Importer():
    """
    Class to handle the package that is uploaded and wants to be imported into
    the database.
    """
    def __init__(self, spool=None, skip_email=False,
                 skip_gpg=False):
        """
        Object constructor. Sets class fields to sane values.

        ``spool``
            Spool directory to process.
        ``skip_email``
            If this is set to true, send no email.
        ``skip_gpg``
            If this is set to true, disable gpg validation.
        """
        self.actually_send_email = not bool(skip_email)
        self.skip_gpg = skip_gpg
        self.repository = Repository(settings.REPOSITORY)
        git_storage_path = getattr(settings, 'GIT_STORAGE', None)
        self.git_storage = GitStorage(git_storage_path)

        if spool:
            self.spool = Spool(spool)

    def process_spool(self):
        """
        Find all incoming uploads in the spool and process them
        """
        success = True

        for changes in self.spool.changes_to_process():
            try:
                upload = self.process_upload(changes)
            except ExceptionImporterRejected as e:
                success = False
                self._reject(e)

            # Unfortunatly, we cannot really test that since it is not supposed
            # to happen. Note that the _fail() method is covered by the tests.
            except Exception as e:  # pragma: no cover
                success = False
                log.error(f'Importing {changes} failed with an unknown error: ')
                log.exception(e)
                self._fail(ExceptionImporterRejected(changes, 'Importer failed',
                                                     e))
            else:
                self._accept(upload)
            finally:
                changes.remove()

        if self.repository:
            self.repository.update()

        return success

    def _is_valid_email(self, email):
        if '<' in email and '>' in email:
            email = email.split('<')[1].split('>')[0]

        try:
            validate_email(email)
        except ValidationError:
            return False

        return True

    def send_email(self, template, error=None, upload=None,
                   notify_admins=False):
        recipients = []

        if not self.actually_send_email:
            log.info(f'Skipping email send: {template} {error}')
            return

        # That should not happen
        if bool(error) == bool(upload):  # pragma: no cover
            log.error(f'Trying to send an import email with error: {error} and'
                      f' upload {upload}')
            return

        email = Email(template)

        if error:
            user = getattr(error.changes, 'uploader', None)

            if user:
                if isinstance(user, User):
                    recipients.append(user.email)
                else:
                    if self._is_valid_email(user):
                        recipients.append(user)

            subject = f'{str(error.changes)}: REJECTED'

        if upload:
            recipients.append(upload.uploader.email)
            subject = f'{upload.package.name}_{upload.version}: ACCEPTED ' \
                      f'into {upload.distribution.name}'

        if notify_admins:
            recipients.append(settings.DEFAULT_FROM_EMAIL)

        log.debug(f'Sending importer mail to {", ".join(recipients)}')
        email.send(subject, recipients,
                   upload=upload, error=error, settings=settings)

    def _accept(self, upload):
        log.info(f'Package {upload.package.name}_{upload.version} accepted '
                 f'into {upload.distribution.name}')
        self.send_email('email-importer-accept.html', upload=upload)

    def _fail(self, error):
        """
        Fail the upload by sending a reason for failure to the log and then
        remove all uploaded files.

        A package is `fail`ed if there is a problem with debexpo, **not** if
        there's something wrong with the package.

        ``error``
            Exception detailing why it failed.
        """
        log.critical(error)
        self.send_email('email-importer-fail.html', error, notify_admins=True)

    def _reject(self, error):
        """
        Reject the package by sending a reason for failure to the log and then
        remove all uploaded files.

        A package is `reject`ed if there is a problem with the package.

        ``error``
            Exception detailing why it failed.
        """
        log.error(error)
        self.send_email('email-importer-reject.html', error)

    @transaction.atomic
    def _create_db_entries(self, changes, source, plugins, git_ref):
        """
        Create entries in the Database for the package upload.
        """
        upload = PackageUpload.objects.create_from_changes(changes)
        upload.git_ref = git_ref
        upload.full_clean()
        upload.save()

        package = source.control.get_source_package()
        source_package = SourcePackage.objects.create_from_package(upload,
                                                                   package)
        source_package.full_clean()
        source_package.save()

        for package in source.control.get_binary_packages():
            binary_package = BinaryPackage.objects.create_from_package(upload,
                                                                       package)
            binary_package.full_clean()
            binary_package.save()

        for result in plugins.results:
            result.upload = upload
            result.full_clean()
            result.save()

            if result.plugin == 'debian-qa':
                upload.package.in_debian = result.data['in_debian']
                upload.package.full_clean()
                upload.package.save()

        return upload

#     def _overlap_with_other_distrib(self):
#         name = self.changes['Source']
#         version = self.changes['Version']
#         distribution = self.changes['Distribution']
#
#         package = meta.session.query(Package).filter_by(name=name).first()
#
#         if package:
#             if meta.session.query(PackageVersion) \
#                     .filter(PackageVersion.version == version,
#                             PackageVersion.distribution != distribution,
#                             PackageVersion.package == package).all():
#                 self._reject('An upload with the same version but '
#                              'different distribution exists on mentors.\n'
#                              'If you wish to upload this version for an '
#                              'other distribution, delete the old '
#                              'one.')
#
#                 return True
#
#         return False
#
    def process_upload(self, changes):
        """
        Actually start the import of the package.

        Do several environment sanity checks, move files into the right place,
        and then create the database entries for the imported package.
        """
        plugins = PluginManager()

        self._validate_changes(changes)
        self._validate_dsc(changes)
        source = self._validate_source(changes)
        plugins.run(changes, source)
        upload = self._accept_upload(changes, source, plugins)
        return upload

    def _accept_upload(self, changes, source, plugins):
        git_ref = None

        # Install source in git tree
        if self.git_storage:
            git_ref = self.git_storage.install(source)

        # Install to repository
        if self.repository:
            self.repository.install(changes)

        # Create DB entries
        upload = self._create_db_entries(changes, source, plugins, git_ref)

        return upload

    def _validate_changes(self, changes):
        # Check that all files referenced in the changelog are present and
        # match their checksum
        try:
            changes.validate()
            if not self.skip_gpg:
                changes.authenticate()
            changes.files.validate()
            changes.get_bugs()
        except (ExceptionChanges, ExceptionCheckSumedFile, ExceptionGnuPG) as e:
            raise ExceptionImporterRejected(changes, 'Changes is invalid', e)

    def _validate_dsc(self, changes):
        # Try parsing dsc file
        try:
            changes.parse_dsc()
        except ExceptionChanges as e:
            raise ExceptionImporterRejected(changes, 'Dsc failed to parse', e)

        # Validate dsc fields, gpg signature and files (including checksuming)
        dsc = changes.dsc

        try:
            dsc.validate()
            if not self.skip_gpg:
                dsc.authenticate()
            dsc.fetch_origin()
            dsc.files.validate()
        except (ExceptionDsc, ExceptionCheckSumedFile, ExceptionGnuPG,
                ExceptionOrigin, ExceptionClient) as e:
            raise ExceptionImporterRejected(changes, 'Dsc is invalid', e)

    def _validate_source(self, changes):
        # Instanciate the source package
        source = Source(changes.dsc)

        # Extract
        try:
            source.extract()
        except ExceptionSource as e:
            raise ExceptionImporterRejected(changes,
                                            'Failed to extract source package',
                                            e)

        # Parse control files (d/changelog, d/copyright and d/control)
        try:
            source.parse_control_files()
        except ExceptionSource as e:
            raise ExceptionImporterRejected(changes,
                                            'Source package is invalid',
                                            e)

        # And valid them
        try:
            source.changelog.validate()
            source.copyright.validate()
            source.control.validate()
        except (ExceptionChangelog, ExceptionCopyright, ExceptionControl) as e:
            raise ExceptionImporterRejected(changes,
                                            'Source package is invalid',
                                            e)

        # Validate distribution
        distribution = changes.distribution
        try:
            Distribution.objects.get(name=distribution)
        except Distribution.DoesNotExist:
            allowed = "\n".join(list(map(str, Distribution.objects.all())))
            raise ExceptionImporterRejected(
                changes, 'Invalid distribution',
                f'Distribution {distribution} is not supported on '
                f'mentors\n\n'
                f'List of supported distributions:\n\n'
                f'{allowed}')

        return source

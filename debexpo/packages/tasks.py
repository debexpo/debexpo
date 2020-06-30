#   tasks.py -- task to remove old and uploaded packages from Debexpo
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2011 Arno Töll <debian@toell.net>
#   Copyright © 2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

# from celery.task import PeriodicTask
from celery.decorators import periodic_task
from datetime import timedelta, datetime, timezone

from django.conf import settings
from django.db.models import Max

from debexpo.packages.models import Package, PackageUpload
from debexpo.repository.models import Repository
from debexpo.tools.email import Email
from debexpo.bugs.models import Bug
from debexpo.tools.gitstorage import GitStorage
# from debexpo.comments.models import PackageSubscription
# from debexpo.accounts.models import User


def remove_uploads(uploads):
    removals = set()
    repository = Repository(settings.REPOSITORY)
    git_storage_path = getattr(settings, 'GIT_STORAGE', None)

    for upload in uploads:
        remove_version = not PackageUpload.objects.filter(
            package=upload.package, version=upload.version) \
            .exclude(id=upload.id)
        remove_package = not PackageUpload.objects.filter(
            package=upload.package).exclude(id=upload.id)
        package = upload.package.name
        distribution = upload.distribution.name
        uploader = upload.uploader

        if remove_version:
            repository.remove(package, upload.version)
        if remove_package:
            if git_storage_path:
                git_storage = GitStorage(git_storage_path, package)
                git_storage.remove()

            Bug.objects.remove_bugs(package)

        upload.delete()

        if remove_package:
            Package.objects.get(name=package).delete()

        removals.add((package, distribution, uploader))

    repository.update()

    return removals


@periodic_task(run_every=settings.TASK_OLD_UPLOADS_BEAT)
def remove_old_uploads():
    expiration_date = datetime.now(timezone.utc) - \
        timedelta(weeks=settings.MAX_AGE_UPLOAD_WEEKS)
    packages = Package.objects \
        .values('name', 'packageupload__distribution') \
        .annotate(latest_upload=Max('packageupload__uploaded')) \
        .filter(latest_upload__lt=expiration_date)

    uploads = set()
    from logging import getLogger
    log = getLogger(__name__)

    for package in packages:
        uploads.update(PackageUpload.objects.filter(
            package__name=package['name'],
            distribution=package['packageupload__distribution']))

    log.debug(f'uploads to remove: {uploads}')

    removals = remove_uploads(uploads)

    for package, distribution, uploader in removals:
        email = Email('email-upload-removed.html')
        email.send(f'{package} has been removed from '
                   f'{distribution} on {settings.SITE_NAME}',
                   recipients=[uploader.email], package=package,
                   distribution=distribution,
                   reason="Your package found no sponsor for "
                          "20 weeks")


# class RemoveAcceptedUploads(PeriodicTask):
#     run_every = settings.TASK_ACCEPT_UPLOADS_BEAT
#
#     def _process_changes(self, mail):
#         if mail.is_multipart():
#             self.log.debug("Changes message is multipart?!")
#             return
#         changes = mail.get_payload(decode=True)
#         try:
#             changes = deb822.Changes(changes)
#         except Exception:
#             self.log.error('Could not open changes file; skipping mail "%s"' %
#                            (mail['subject']))
#             return
#
#         if 'Source' not in changes:
#             # self.log.debug('Changes file "%s" seems incomplete' %
#             #               (mail['subject']))
#             return
#
#         package = self.pkg_controller._get_package(changes['Source'],
#                                                    from_controller=False)
#         if package is not None:
#             for pv in package.package_versions:
#                 if pv.distribution == changes['Distribution']:
#                     if (apt_pkg.version_compare(changes['Version'],
#                                                 pv.version)
#                             == 0):
#                         self.log.debug("Package %s was uploaded to Debian - "
#                                        "removing it from Expo" %
#                                        (changes['Source']))
#                         self._remove_package(package, pv,
#                                              "Package was uploaded to "
#                                              "official Debian repositories")
#                     if (apt_pkg.version_compare(changes['Version'],
#                                                 pv.version)
#                             > 0):
#                         self.log.debug("More recent package %s was uploaded "
#                                        "to Debian - removing it from Expo" %
#                                        (changes['Source']))
#                         self._remove_package(package, pv,
#                                              "A more recent package was "
#                                              "uploaded to official Debian "
#                                              "repositories")
#         else:
#             # self.log.debug("Package %s was not uploaded to Expo before - "
#             #                "ignoring it" % (changes['Source']))
#             pass
#
#     def _remove_uploaded_packages(self):
#
#         if self.mailer.connection_established():
#             lists = meta.session.query(DataStore) \
#                     .filter(DataStore.namespace == __namespace__) \
#                     .all()
#             for list_name in lists:
#                 for message in self.mailer.unread_messages(list_name.code,
#                                                            list_name.value):
#                     self._process_changes(message)
#                     list_name.value = message['X-Debexpo-Message-Number']
#                 self.log.debug("Processed all messages up to #%s on %s" %
#                                (list_name.value, list_name.code))
#                 meta.session.merge(list_name)
#             meta.session.commit()
#             self.mailer.disconnect_from_server()
#
#     def _remove_old_packages(self):
#         now = datetime.datetime.now()
#         for package in self.pkgs_controller._get_packages():
#             if (now - package.package_versions[-1].uploaded) > \
#                     datetime.timedelta(weeks=20):
#                 self.log.debug("Removing package %s - uploaded on %s" %
#                                (package.name,
#                                 package.package_versions[-1].uploaded))
#                 for pv in package.package_versions:
#                     self._remove_package(package, pv,
#                                          "Your package found no sponsor for "
#                                          "20 weeks")
#
#     def setup(self):
#         self.mailer = Email('upload_removed_from_expo')
#         self.mailer.connect_to_server()
#         self.pkg_controller = PackageController()
#         self.pkgs_controller = PackagesController()
#         apt_pkg.init_system()
#         self.log.debug("%s loaded successfully" % (__name__))
#
#     def teardown(self):
#         self.mailer.disconnect_from_server()
#
#     def invoke(self):
#         try:
#             self._remove_uploaded_packages()
#         except socket.error as e:
#             # better luck next time
#             self.log.debug("Socket error %s: skipping removals his time"
#                            % (e))
#             pass
#
#         # We don't need to run our garbage collection of old cruft that often
#         # It's ok if we purge old packages once a day.
#         if (datetime.datetime.now() - self.last_cruft_run) >= \
#                 datetime.timedelta(hours=24):
#             self.last_cruft_run = datetime.datetime.now()
#             self._remove_old_packages()
#
#
# cronjob = RemoveOldUploads
# schedule = datetime.timedelta(minutes=10)

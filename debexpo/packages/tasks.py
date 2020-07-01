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

from celery.decorators import periodic_task
from datetime import timedelta, datetime, timezone
from logging import getLogger
from debian.deb822 import Changes
from debian.debian_support import NativeVersion

from django.conf import settings
from django.db.models import Max

from debexpo.packages.models import Package, PackageUpload
from debexpo.repository.models import Repository
from debexpo.tools.email import Email
from debexpo.bugs.models import Bug
from debexpo.tools.gitstorage import GitStorage
from debexpo.nntp.models import NNTPFeed
from debexpo.tools.nntp import NNTPClient

log = getLogger(__name__)


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
    notify_uploaders(removals, reason='Your package found no sponsor for '
                                      '20 weeks')


def notify_uploaders(removals, reason):
    for package, distribution, uploader in removals:
        email = Email('email-upload-removed.html')
        email.send(f'{package} has been removed from '
                   f'{distribution} on {settings.SITE_NAME}',
                   recipients=[uploader.email], package=package,
                   distribution=distribution,
                   reason=reason)


@periodic_task(run_every=settings.TASK_ACCEPTED_UPLOADS_BEAT)
def remove_uploaded_packages(client=None):
    feeds = NNTPFeed.objects.filter(namespace='remove_uploads')
    uploads = set()

    # We allow the caller to define another NNTPClient, if not fallback to the
    # default one. This is for testing purposes only: easier than setting up a
    # testing NNTP server.
    if not client:  # pragma: no cover
        client = NNTPClient()

    if not client.connect_to_server():
        return

    for feed in feeds:
        last = feed.last

        for msg in client.unread_messages(feed.name, feed.last):
            try:
                uploads.update(process_accepted_changes(msg))
            except Exception as e:
                log.warning('Failed to process message after '
                            f'#{last} on '
                            f'{feed.name}: {str(e)}')
            else:
                last = msg['X-Debexpo-Message-Number']

        feed.last = last

    client.disconnect_from_server()
    removals = remove_uploads(uploads)
    notify_uploaders(removals, reason='Your package was uploaded to the '
                                      'official Debian archive')

    for feed in feeds:
        feed.full_clean()
        feed.save()


def process_accepted_changes(mail):
    if not mail or mail.is_multipart():
        return

    changes = mail.get_payload(decode=True)
    changes = Changes(changes)

    if 'Source' not in changes \
            or 'Distribution' not in changes \
            or 'Version' not in changes:
        raise Exception(f'Missing required keys in changes: {changes}')

    uploads = PackageUpload.objects.filter(
        package__name=changes['Source'],
        distribution__name=changes['Distribution'])

    return [
        upload for upload in uploads
        if NativeVersion(upload.version) <= NativeVersion(changes['Version'])
    ]

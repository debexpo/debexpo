#   views.py — packages views
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#               2011 Arno Töll <debian@toell.net>
#               2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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

import logging
import datetime

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect, \
    HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _, get_language
from django.contrib.syndication.views import Feed
from django.contrib.auth.decorators import login_required
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from debexpo.packages.models import PackageUpload, Package, SourcePackage
from debexpo.packages.serializers import PackageSerializer, \
    PackageUploadSerializer
from debexpo.comments.forms import CommentForm
from debexpo.repository.tasks import remove_from_repository
from debexpo.tools.gitstorage import GitStorage
from debexpo.bugs.models import Bug
from debexpo.packages.tasks import remove_uploads

log = logging.getLogger(__name__)

LIST_MODELS = [
    'distribution',
    'component',
    'section',
    'priority',
]


class PackageGroups(object):
    """
    A helper class to hold packages matching a certain time criteria
    """
    def __init__(self, label, deltamin, deltamax, packages):
        self.label = label
        self.packages = []

        if (deltamin is not None and deltamax is not None):
            self.packages = [
                x for x in packages if
                x.packageupload_set.latest('uploaded').uploaded <= deltamin and
                x.packageupload_set.latest('uploaded').uploaded > deltamax
            ]
        elif (deltamin is None and deltamax is not None):
            self.packages = [
                x for x in packages if
                x.packageupload_set.latest('uploaded').uploaded > deltamax
            ]
        elif (deltamin is not None and deltamax is None):
            self.packages = [
                x for x in packages if
                x.packageupload_set.latest('uploaded').uploaded <= deltamin
            ]


def _get_packages(key=None, value=None):
    """
    Returns a list of packages that fit the filters.

    ``key``
        Any key of a Package, PackageUpload or SourcePackage

    ``value``
        Corresponding value to filter by
    """
    query = Package.objects
    name = key

    # Use name lookup for 'list' models
    if key in LIST_MODELS:
        key = '{}__name'.format(key)

    # Use email lookup for uploader
    if key == 'uploader':
        key = 'uploader__email'

    if name in [f.name for f in Package._meta.get_fields()]:
        query = query.filter(**{key: value})
    elif name in [f.name for f in PackageUpload._meta.get_fields()]:
        query = query.filter(**{'packageupload__' + key: value})
    elif name in [f.name for f in SourcePackage._meta.get_fields()]:
        query = query.filter(**{'packageupload__sourcepackage__' + key: value})
    elif name is not None:
        query = query.none()
        log.warning('Could not apply filter: %s', key)

    return set(query.all())


def _get_timedeltas(packages):
    deltas = []
    now = datetime.datetime.now(datetime.timezone.utc)
    deltas.append(PackageGroups(_("Today"), None, now -
                                datetime.timedelta(days=1),
                                packages))
    deltas.append(PackageGroups(_("Yesterday"), now -
                                datetime.timedelta(days=1),
                                now - datetime.timedelta(days=2),
                                packages))
    deltas.append(PackageGroups(_("Some days ago"), now -
                                datetime.timedelta(days=2),
                                now - datetime.timedelta(days=7),
                                packages))
    deltas.append(PackageGroups(_("Older packages"), now -
                                datetime.timedelta(days=7),
                                now - datetime.timedelta(days=30),
                                packages))
    deltas.append(PackageGroups(_("Uploaded long ago"), now -
                                datetime.timedelta(days=30),
                                None, packages))
    return deltas


def package(request, name):
    package = get_object_or_404(Package, name=name)
    form = CommentForm()

    return render(request, 'package.html', {
        'settings': settings,
        'package': package,
        'comment_form': form,
    })


@login_required
def delete_upload(request, name, upload):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    upload = get_object_or_404(PackageUpload, id=upload)
    package = upload.package.name

    if (request.user != upload.uploader and not
            request.user.is_superuser):
        return HttpResponseForbidden()

    remove_uploads([upload])

    try:
        Package.objects.get(name=package)
    except Package.DoesNotExist:
        return HttpResponseRedirect(reverse('packages_my'))
    else:
        return HttpResponseRedirect(reverse('package', args=[package]))


@login_required
def delete_package(request, name):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    package = get_object_or_404(Package, name=name)

    if (request.user not in package.get_uploaders() and not
            request.user.is_superuser):
        return HttpResponseForbidden()

    package.delete()
    log.info('Package deleted: {}'.format(name))

    git_storage_path = getattr(settings, 'GIT_STORAGE', None)

    if git_storage_path:
        git_storage = GitStorage(git_storage_path, name)
        git_storage.remove()

    remove_from_repository.delay(name)
    Bug.objects.remove_bugs(package)

    return HttpResponseRedirect(reverse('packages_my'))


@login_required
def sponsor_package(request, name):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    package = get_object_or_404(Package, name=name)

    if request.user not in package.get_uploaders():
        return HttpResponseForbidden()

    package.needs_sponsor = not package.needs_sponsor
    package.full_clean()
    package.save()
    log.info('Toogle needs sponsor for: {} ({})'.format(name,
                                                        package.needs_sponsor))

    return HttpResponseRedirect(reverse('package', args=[name]))


def packages(request, key=None, value=None):
    # List of packages to show in the page.
    packages = _get_packages(key, value)
    feed = request.build_absolute_uri() + 'feed/'

    if key:
        title = _('Packages for {} {}').format(key, value)
    else:
        title = _('Package list')

    # Render the page.
    return render(request, 'packages.html', {
        'settings': settings,
        'packages': packages,
        'deltas': _get_timedeltas(packages),
        'package_title': title,
        'feed_url': feed
    })


class PackagesFeed(Feed):
    title = _('%s packages' % settings.SITE_NAME)
    description = _('A feed of packages on %s' % settings.SITE_NAME)
    language = get_language()

    def get_object(self, request, key=None, value=None, feed=None):
        self.request = request
        return _get_packages(key, value)

    def link(self, packages):
        return self.request.build_absolute_uri(reverse('packages'))

    def items(self, packages):
        return packages

    def item_title(self, item):
        return '%s %s' % (
            item.name, item.packageupload_set.latest('uploaded').version)

    def item_link(self, item):
        return self.request.build_absolute_uri(
                reverse('package', kwargs={'name': item.name}))

    def item_description(self, item):
        desc = _('Package {} uploaded by {}.').format(
            item.name,
            item.packageupload_set.latest('uploaded').uploader.name)
        desc += '<br/><br/>'

        if item.needs_sponsor:
            desc += _('Uploader is currently looking for a sponsor.')
        else:
            desc += _('Uploader is currently not looking for a sponsor.')

        binary_package = item.packageupload_set.latest('uploaded') \
            .binarypackage_set.filter(name=item.name)

        if binary_package:
            desc += '<br/><br/>' + binary_package.get().description \
                    .replace('\n', '<br/>')

        return desc


@login_required
def packages_my(request):
    return packages(request, 'uploader', request.user.email)


class PackageViewSet(NestedViewSetMixin, ReadOnlyModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    filterset_fields = set(serializer_class.Meta.fields) \
        .difference(('uploaders', 'versions', 'id',))


class PackageUploadViewSet(NestedViewSetMixin, ReadOnlyModelViewSet):
    queryset = PackageUpload.objects.all()
    serializer_class = PackageUploadSerializer
    filterset_fields = set(serializer_class.Meta.fields) \
        .difference(('id', 'distribution', 'component', 'closes', 'uploader',
                     'package'))

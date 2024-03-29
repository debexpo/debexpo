#   models.py - Packages models (Package, PackageVersion, SourcePackage,
#   BinaryPackage)
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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

import json
from os.path import join

from django.db import models
from django.utils.translation import gettext_lazy as _

from debexpo.accounts.models import User
from debexpo.repository.models import RepositoryFile


class Project(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Name'), unique=True)

    def __str__(self):
        return self.name


class Distribution(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Name'), unique=True)
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Component(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Name'), unique=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Name'), unique=True)

    def __str__(self):
        return self.name


class Priority(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Name'), unique=True)

    def __str__(self):
        return self.name


class PackageUploadManager(models.Manager):
    def create_from_changes(self, changes):
        upload = PackageUpload()

        upload.package = Package.objects.get_or_create(
            name=changes.source)[0]
        upload.uploader = changes.uploader

        upload.version = changes.version
        upload.distribution = Distribution.objects.get(
            name=changes.distribution)
        upload.component = Component.objects.get_or_create(
            name=changes.files.files[0].component)[0]
        upload.changes = changes.changes
        upload.closes = changes.closes

        return upload


class PackageManager(models.Manager):
    def create_from_package(self, upload, package):
        if isinstance(self.model(), SourcePackage):
            entry = SourcePackage()

            entry.maintainer = package['maintainer']
        else:
            entry = BinaryPackage()

            entry.name = package['package']
            entry.architecture = package['architecture']
            entry.description = package['description'].split('\n')[0]

        entry.upload = upload
        entry.homepage = package.get('homepage')

        if package.get('section'):
            entry.section = Section.objects.get_or_create(
                name=package.get('section'))[0]

        if package.get('priority'):
            entry.priority = Priority.objects.get_or_create(
                name=package.get('priority'))[0]

        entry.vcs = json.dumps(self._get_vcs_fields(package))

        return entry

    def _get_vcs_fields(self, package):
        vcs = {}

        for attribute in package:
            if attribute.lower().startswith('vcs-'):
                vcs[attribute] = package[attribute]

        return vcs


class Package(models.Model):
    # At the time of writing, longest package name is 60 in bullseye/sid
    name = models.CharField(max_length=100, verbose_name=_('Name'), unique=True)
    needs_sponsor = models.BooleanField(default=False,
                                        verbose_name=_('Needs a sponsor?'))
    in_debian = models.BooleanField(default=False, verbose_name=_('In Debian?'))

    def __str__(self):
        return self.name

    def get_description(self):
        upload = self.packageupload_set.latest('uploaded')

        if upload.binarypackage_set.count():
            binary = upload.binarypackage_set.filter(name=self.name)

            if not binary:
                binary = upload.binarypackage_set.last()
                return binary.description
            else:
                return binary.get().description

        return ''

    def get_full_description(self):
        description = []
        upload = self.packageupload_set.latest('uploaded')

        for binary in upload.binarypackage_set.all():
            description.append('{} - {}'.format(binary.name,
                                                binary.description))

        return '\n'.join(description)

    def get_versions(self):
        versions = {}

        for item in self.packageupload_set.order_by('uploaded').values(
                'version', 'distribution__name'):
            versions[item['distribution__name']] = item['version']

        return versions

    def format_versions(self):
        return '\n'.join(['{} ({})'.format(version, distribution) for
                          distribution, version in self.get_versions().items()])

    def get_uploaders(self):
        return set([
            User.objects.get(pk=item['uploader'])
            for item in self.packageupload_set.values('uploader')
        ])


class PackageUpload(models.Model):
    class Meta:
        ordering = ['-uploaded']

    objects = PackageUploadManager()
    # Links a package and a user (as uploader)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)

    # The following is extracted from the .changes
    # At the time of writing, longest version string is 55 in bullseye/sid
    version = models.CharField(max_length=100, verbose_name=_('Version'))
    distribution = models.ForeignKey(Distribution, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    changes = models.TextField(verbose_name=_('Changes'))
    closes = models.TextField(blank=True, verbose_name=_('Closes bugs'))
    git_ref = models.TextField(blank=True, null=True,
                               verbose_name=_('Git storage ref'))

    # Some metadata
    uploaded = models.DateTimeField(verbose_name=_('Upload date'),
                                    auto_now_add=True)

    def get_closes(self):
        return self.closes.split()

    def get_index(self):
        return PackageUpload.objects.filter(
            package=self.package, uploaded__lt=self.uploaded).count() + 1

    def get_dsc_url(self):
        try:
            dsc = RepositoryFile.objects.get(
                package=self.package.name,
                version=self.version,
                distribution=self.distribution.name,
                path__endswith='.dsc'
            )
        except RepositoryFile.DoesNotExist:
            return

        return join('/', 'debian', str(dsc))

    def get_dsc_name(self):
        dsc = self.get_dsc_url()

        if dsc:
            return dsc.split('/')[-1]


class SourcePackage(models.Model):
    # Links a PackageUpload
    upload = models.ForeignKey(PackageUpload, on_delete=models.CASCADE)

    # Mandatory
    # At the time of writing, longest maintainer string is 91 in bullseye/sid
    maintainer = models.CharField(max_length=120, verbose_name=_('Maintainer'))

    # Optional
    section = models.ForeignKey(Section, null=True, blank=True,
                                on_delete=models.SET_NULL)
    priority = models.ForeignKey(Priority, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    homepage = models.TextField(null=True, blank=True,
                                verbose_name=_('Homepage'))
    vcs = models.TextField(null=True, blank=True, verbose_name=_('VCS'))

    objects = PackageManager()

    def get_vcs(self):
        if not self.vcs:
            return []

        vcs = json.loads(self.vcs)

        return vcs.items()

    def get_vcs_browser(self):
        for key, value in self.get_vcs():
            if key.lower() == 'vcs-browser':
                return value


class BinaryPackage(models.Model):
    # Links a PackageUpload
    upload = models.ForeignKey(PackageUpload, on_delete=models.CASCADE)

    # Mandatory
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(verbose_name=_('Description'))

    # Optional
    section = models.ForeignKey(Section, null=True, blank=True,
                                on_delete=models.SET_NULL)
    priority = models.ForeignKey(Priority, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    homepage = models.TextField(null=True, blank=True,
                                verbose_name=_('Homepage'))

    objects = PackageManager()

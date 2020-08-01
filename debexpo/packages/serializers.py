#   serializers.py - API definition for packages
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
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

from debexpo.packages.models import Package, PackageUpload
from rest_framework.serializers import ModelSerializer, CharField, ListField, \
    IntegerField, DictField


class PackageSerializer(ModelSerializer):
    versions = DictField(source='get_versions')
    uploaders = ListField(source='get_uploaders', child=CharField())

    class Meta:
        model = Package
        fields = (
            'id',
            'name',
            'in_debian',
            'needs_sponsor',
            'uploaders',
            'versions',
        )
        lookup_field = 'id'


class PackageUploadSerializer(ModelSerializer):
    distribution = CharField(source='distribution.name')
    component = CharField(source='component.name')
    closes = ListField(source='get_closes', child=IntegerField())
    uploader = CharField(source='uploader.email')
    package_id = IntegerField(source='package.id')
    package = CharField(source='package.name')

    class Meta:
        model = PackageUpload
        fields = (
            'id',
            'changes',
            'closes',
            'component',
            'distribution',
            'package',
            'package_id',
            'uploaded',
            'uploader',
            'version',
        )
        lookup_field = 'id'

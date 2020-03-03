#   models.py - models for plugins
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#               2020 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from enum import Enum
from json import dumps, loads
from os.path import abspath, dirname, isfile, join

from django.db import models
from django.utils.translation import gettext_lazy as _

from debexpo.packages.models import PackageUpload


class PluginSeverity(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.tuple = (value, label)
        return obj

    info = (1, _('Infomation'))
    warning = (2, _('Warning'))
    error = (3, _('Error'))
    critical = (4, _('Critical'))
    failed = (5, _('Failed'))

    @classmethod
    def as_tuple(cls):
        return (cls.info.tuple,
                cls.warning.tuple,
                cls.error.tuple,
                cls.critical.tuple,
                cls.failed.tuple,)


class PluginResults(models.Model):
    upload = models.ForeignKey(PackageUpload, on_delete=models.CASCADE)

    plugin = models.TextField(verbose_name=_('Plugin name'))
    test = models.CharField(max_length=32, verbose_name=_('Test identifier'))
    outcome = models.TextField(verbose_name=_('Outcome'))
    json = models.TextField(null=True, verbose_name=_('Data'))
    severity = models.PositiveSmallIntegerField(
        verbose_name=_('Severity'), choices=PluginSeverity.as_tuple()
    )

    @property
    def template(self):
        template = join(dirname(abspath(__file__)), 'templates',
                        f'plugin-{self.plugin}.html')
        if isfile(template):
            return self.plugin

        return 'plugin-default.html'

    @property
    def data(self):
        return loads(self.json)

    @data.setter
    def data(self, data):
        self.json = dumps(data)

    def get_severity(self):
        return PluginSeverity(self.severity).label

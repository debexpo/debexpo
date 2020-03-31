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

from abc import ABCMeta, abstractmethod
from logging import getLogger
from enum import Enum
from json import dumps, loads
from os.path import abspath, dirname, isfile, join

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from debexpo.packages.models import PackageUpload
from debexpo.tools.debian.changes import Changes
from debexpo.tools.debian.source import Source

log = getLogger(__name__)


class ExceptionPlugin(Exception):
    pass


class PluginSeverity(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.tuple = (value, label)
        return obj

    info = (1, _('Information'))
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
    test = models.TextField(verbose_name=_('Test identifier'))
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
            return f'plugin-{self.plugin}.html'

        return 'plugin-default.html'

    @property
    def data(self):
        return loads(self.json)

    @data.setter
    def data(self, data):
        self.json = dumps(data)

    def get_severity(self):
        return PluginSeverity(self.severity).label


class PluginManager():
    def __init__(self):
        self.plugins = []

        self._load_plugins()

    def _load_plugins(self):
        for module_name, class_name in settings.IMPORTER_PLUGINS:
            # Import and instantiate the plugin
            try:
                module = __import__(module_name, globals(), locals(),
                                    [class_name], 0)
                self.plugins.append(getattr(module, class_name)())
            except Exception as e:
                log.warning(f'Failed to load plugin {class_name} from '
                            f'{module_name}: {e}')

    def run(self, changes, source):
        for plugin in self.plugins:
            try:
                plugin.run(changes, source)
            except Exception as e:
                log.warning(f'Plugin {plugin.name} failed: {str(e)}')
                plugin.add_result(plugin.name, str(e), None,
                                  PluginSeverity.failed)

    @property
    def results(self):
        results = []

        for plugin in self.plugins:
            results += plugin.results

        return results


class BasePlugin(metaclass=ABCMeta):
    def __init__(self):
        self.results = []

    @property
    @abstractmethod
    def name(self):
        # We cannot cover abstract methods
        pass  # pragma: nocover

    @abstractmethod
    def run(self, changes: Changes, source: Source):
        # We cannot cover abstract methods
        pass  # pragma: nocover

    def add_result(self, test, outcome, data=None, severity=None):
        """
        Adds a PluginResult for a passed test to the result list.

        ``test``
            Test identifier,

        ``outcome``
            Outcome tag of the test.

        ``data``
            Resulting data from the plugin, like more details about the process.

        ``severity``
            Severity of the result.
        """
        if not severity:
            severity = PluginSeverity.info

        self.results.append(PluginResults(
            plugin=self.name,
            test=test,
            outcome=outcome,
            data=data,
            severity=severity,
        ))

    def failed(self, reason):
        """
        Fail the plugin by raising an ExceptionPlugin

        ``reason``
            An explainaition to why the plugin failed
        """
        self.results = []

        raise ExceptionPlugin(reason)

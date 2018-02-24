# -*- coding: utf-8 -*-
#
#   __init__.py — Helpful classes for plugins
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
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

"""
Holds some helpful classes for plugins to use or extend.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

from debexpo.lib import constants

class BasePlugin(object):
    """
    The class all other plugins should extend.
    """

    def __init__(self, **kw):
        """
        Class constructor. Sets class attributes depending on the arguments of the
        constructor.

        ``kw``
            Values to assign to class attributes.
        """
        for key in kw:
            setattr(self, key, kw[key])

    def run(self):
        """
        Runs all the tests in the self.tests list.
        """
        self.result = []
        for method in dir(self):
            if method.startswith('test'):
                getattr(self, method)()

        return self.result

    def passed(self, outcome, data, severity):
        """
        Adds a PluginResult for a passed test to the result list.

        ``outcome``
            Outcome tag of the test.

        ``data``
            Resulting data from the plugin, like more details about the process.

        ``severity``
            Severity of the result.
        """
        self.result.append(PluginResult(from_plugin=self.name, outcome=outcome,
            data=data, severity=severity))

    def failed(self, outcome, data, severity):
        """
        Adds a PluginResult for a failed test to the result list.

        ``outcome``
            Outcome tag of the test.

        ``data``
            Resulting data from the plugin, like more details about the process.

        ``severity``
            Severity of the result.

        """
        self.result.append(PluginResult(from_plugin=self.name, outcome=outcome,
            data=data, severity=severity))

    def info(self, outcome, data):
        """
        Adds a PluginResult for an info test to the result list.

        ``outcome``
            Outcome tag of the test.

        ``data``
            Resulting data from the plugin, like more detail about the process.
        """
        self.result.append(PluginResult(from_plugin=self.name, outcome=outcome,
            data=data, severity=constants.PLUGIN_SEVERITY_INFO))

class PluginResult(object):
    """
    The class tests should return to provide details about a test.
    """

    def __init__(self, from_plugin, outcome, data, severity):
        """
        Class constructor. Sets important fields.

        ``from_plugin``
            Name of the plugin the test was carried out in.

        ``outcome``
            Outcome of the test.

        ``data``
            More details of the test.

        ``severity``
            Severity of the result.
        """
        self.from_plugin = from_plugin
        self.outcome = outcome
        self.data = data
        self.severity = severity

    def failed(self):
        """
        Returns whether the test failed.
        """
        return self.severity > constants.PLUGIN_SEVERITY_INFO

    def stop(self):
        """
        Returns whether the process should stop after the test.
        """
        return self.severity >= constants.PLUGIN_SEVERITY_CRITICAL


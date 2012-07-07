# -*- coding: utf-8 -*-
#
#   distribution.py — distribution check plugin
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2012 Nicolas Dandrimont <nicolas.dandrimont@crans.org>
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
Distribution checks.
"""

__author__ = 'Nicolas Dandrimont'
__copyright__ = ', '.join([
        'Copyright © 2012 Nicolas Dandrimont',
        ])
__license__ = 'MIT'

import logging
import os

from debexpo.lib import constants
from debexpo.plugins import BasePlugin

class DistributionPlugin(BasePlugin):

    def test_distribution(self):
        """
        Checks whether the package is for the UNRELEASED distribution
        """

        data = {
            "is-unreleased": False,
            }
        distribution = self.changes["Distribution"]

        if distribution.lower() == "unreleased":
            data["is-unreleased"] = True
            self.failed("Package uploaded for the UNRELEASED distribution", data, constants.PLUGIN_SEVERITY_ERROR)


plugin = DistributionPlugin

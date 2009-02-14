# -*- coding: utf-8 -*-
#
#   ubuntuversion.py — ubuntuversion plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2009 Jonny Lamb <jonny@debian.org>
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
Holds the ubuntuversion plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2009 Jonny Lamb'
__license__ = 'MIT'

import logging

from debexpo.lib.base import *
from debexpo.plugins import BasePlugin
from debexpo.lib import constants

log = logging.getLogger(__name__)

class UbuntuVersionPlugin(BasePlugin):

    def test_ubuntu_version(self):
        """
        Checks whether the word "ubuntu" exists in the package name.
        """
        log.debug('Checking whether the package version contains the word "ubuntu"')

        if 'ubuntu' in self.changes['Version']:
            log.debug('Package does not have ubuntu in the version')
            # This isn't even worth setting an outcome.
        else:
            log.error('Package has ubuntu in the version')
            self.failed('package-has-ubuntu-version', None, constants.PLUGIN_SEVERITY_CRITICAL)

plugin = UbuntuVersionPlugin

outcomes = {
    'package-has-ubuntu-version' : 'The uploaded package has "ubuntu" in the version'
}

# -*- coding: utf-8 -*-
#
#   notuploader.py — notuploader plugin
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
Holds the getorigtarball plugin.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging

from debexpo.plugins import BasePlugin
from debexpo.lib import constants

from debexpo.model import meta
from debexpo.model.packages import Package

from pylons import config

log = logging.getLogger(__name__)

class NotUploaderPlugin(BasePlugin):

    def test_not_uploader(self):
        """
        If there is a package already in the archive with the new package uploaded name,
        make sure it was uploaded by the same uploader.
        """
        packagename = self.changes['Source']
        log.debug('Checking whether %s is in the archive already' % packagename)

        package = meta.session.query(Package).filter_by(name=packagename).first()

        if package is None:
            log.debug('It is not')
            return

        log.debug('It is in the archive; checking whether the uploader is the same as before')

        if package.user_id == int(self.user_id):
            log.debug('Package belongs to uploader')
            # This isn't even worth setting an outcome.
        else:
            log.error('Package does not belong to uploader')
            self.failed('This package was previously uploaded to %s by another user' % config["debexpo.sitename"],
                        None,
                        constants.PLUGIN_SEVERITY_CRITICAL)

plugin = NotUploaderPlugin

# -*- coding: utf-8 -*-
#
#   ppa.py — ppa controller
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
Holds the PPA controller.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import bz2
import logging
import paste.fileapp
import os
import zlib

from debexpo.lib.base import *
from debexpo.lib.repository import Repository

from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion
from debexpo.model.source_packages import SourcePackage
from debexpo.model.binary_packages import BinaryPackage
from debexpo.model.package_files import PackageFile

log = logging.getLogger(__name__)

class PpaController(BaseController):

    def index(self, email):
        """
        Displays information on accessing a user's PPA.

        ``email``
            Email address of user.
        """
        c.user = meta.session.query(User).filter_by(email=email).first()
        c.config = config
        return render('/ppa/index.mako')

    def _create_dists(self, email, filename):
        """
        Create a /dists/... file and return it in the appropraite format.

        ``email``
            Email address to filter on.

        ``filename``
            Filename requested. This should be something like:
            "dists/unstable/main/source/Sources".
        """
        splitfilename = filename.split('/')
        if not len(splitfilename) == 5:
            log.error('File not found')
            abort(404, 'File not found')

        dists, dist, component, arch, type = filename.split('/')

        if arch.startswith('binary-'):
            arch = arch[7:]

        user = meta.session.query(User).filter_by(email=email).first()
        if user is None:
            log.error('User not found')
            abort(404, 'User not found')

        repo = Repository(config['debexpo.repository'])

        if type.startswith('Sources'):
            out_file = repo.get_sources_file(dist, component, user.id)
        elif type.startswith('Packages'):
            out_file = repo.get_packages_file(dist, component, arch, user.id)

        else:
            log.error('File not found')
            abort(404, 'File not found')

        if type.endswith('.gz'):
            return zlib.compress(out_file)
        elif type.endswith('.bz2'):
            return bz2.compress(out_file)
        else:
            return out_file

    def file(self, email, filename):
        """
        Opens a file in the repository using Paste's FileApp.
        """
        log.debug('%s requested' % filename)

        if filename.startswith('dists/'):
            return self._create_dists(email, filename)

        file = os.path.join(config['debexpo.repository'], filename)

        if os.path.isfile(file):
            fapp = paste.fileapp.FileApp(file)
        else:
            log.error('File not found')
            abort(404, 'File not found')

        return fapp(request.environ, self.start_response)

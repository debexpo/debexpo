# -*- coding: utf-8 -*-
#
#   index.py — index controller
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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
Holds the IndexController.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import logging

from debexpo.lib.base import BaseController, c, config, render
from debexpo.controllers.packages import PackagesController, PackageGroups
from webhelpers.html import literal
from datetime import datetime, timedelta
from debexpo.model.package_versions import PackageVersion
from debexpo.model.packages import Package

log = logging.getLogger(__name__)

class IndexController(BaseController):

    def index(self):
        pkg_controller = PackagesController()

        if 'debexpo.html.frontpage' in config:
            f = open(config['debexpo.html.frontpage'])
            c.custom_html = literal(f.read())
            f.close()
        else:
            c.custom_html = ''

        c.config = config
        c.packages = pkg_controller._get_packages(
		        package_version_filter=(PackageVersion.uploaded >= (datetime.today() - timedelta(days=30))),
		        package_filter=(Package.needs_sponsor == 1)
            )
        c.deltas = pkg_controller._get_timedeltas(c.packages)
        c.deltas.pop()
	return render('/index/index.mako')

    def contact(self):
        c.config = config
        return render('/index/contact.mako')

    def qa(self):
        c.config = config
        return render('/index/qa.mako')

    def intro_reviewers(self):
        c.config = config
        return render('/index/reviewers.mako')

    def intro_maintainers(self):
        """Return an introduction page for package maintainers"""
        if 'debexpo.html.maintainer_intro' in config:
            f = open(config['debexpo.html.maintainer_intro'])
            c.custom_html = literal(f.read())
            f.close()
        else:
            c.custom_html = ''

        return render('/index/intro-maintainers.mako')


    def intro_sponsors(self):
        """Return an introduction page for sponsors"""
        if 'debexpo.html.sponsors_intro' in config:
            f = open(config['debexpo.html.sponsors_intro'])
            c.custom_html = literal(f.read())
            f.close()
        else:
            c.custom_html = ''

        return render('/index/intro-sponsors.mako')

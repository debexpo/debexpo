# -*- coding: utf-8 -*-
#
#   index.py — index controller
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
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
import pylons

from debexpo.lib.base import BaseController, c, config, render, session
from debexpo.lib import constants
from debexpo.controllers.packages import PackagesController, PackageGroups
from webhelpers.html import literal
from datetime import datetime, timedelta
from debexpo.model.package_versions import PackageVersion
from debexpo.model.packages import Package
from debexpo.model.users import User

from debexpo.model import meta
from debexpo.model.cronjob_info import CronJobInfo
from babel.dates import format_timedelta
from glob import glob

log = logging.getLogger(__name__)

class IndexController(BaseController):

    def index(self):
        pkg_controller = PackagesController()

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

        # The template will need to look at the user details.
        if 'user_id' in session:
            log.debug('Getting user object for user_id = "%s"' % session['user_id'])
            self.user = meta.session.query(User).get(session['user_id'])
            c.user = self.user
            c.logged_in = True
        else:
            c.logged_in = False

        return render('/index/intro-maintainers.mako')

    def status(self):
        c.config = config
        jobs = []
        for job in meta.session.query(CronJobInfo):
            status = None
            if datetime.now() < job.last_run + timedelta(seconds=job.schedule * 2):
                status = 'info'
            elif datetime.now() < job.last_run + timedelta(seconds=job.schedule * 3):
                status = 'warning'
            else:
                status = 'error'
            message = format_timedelta(job.last_run - datetime.now(), add_direction=True)
            jobs.append({
                'name': job.name,
                'last_run': job.last_run.ctime(),
                'interval': format_timedelta(timedelta(seconds=job.schedule)),
                'status': status,
                'message': message
            })
        c.pending_packages = len(glob(pylons.config['debexpo.upload.incoming'] + 'pub/*.changes'))
        c.jobs = jobs
        return render('/index/status.mako')

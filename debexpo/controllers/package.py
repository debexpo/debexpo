# -*- coding: utf-8 -*-
#
#   package.py — Package controller
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
Holds the PackageController.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

from datetime import datetime
import logging
import os

from debexpo.lib.base import *
from debexpo.lib import constants, form
from debexpo.lib.utils import get_package_dir
from debexpo.lib.email import Email
from debexpo.lib.schemas import PackageSubscribeForm, PackageCommentForm

from debexpo.model import meta
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion
from debexpo.model.users import User
from debexpo.model.package_comments import PackageComment
from debexpo.model.package_info import PackageInfo
from debexpo.model.source_packages import SourcePackage
from debexpo.model.binary_packages import BinaryPackage
from debexpo.model.package_files import PackageFile
from debexpo.model.package_subscriptions import PackageSubscription

log = logging.getLogger(__name__)

class PackageController(BaseController):

    def _get_package(self, packagename):
        """
        """
        log.debug('Details of package "%s" requested' % packagename)

        package = meta.session.query(Package).filter_by(name=packagename).first()

        if package is None:
            log.error('Could not get package information')
            redirect(url(controller='packages', action='index', packagename=None))

        c.package = package
        c.config = config
        c.package_dir = get_package_dir(package.name)
        return package

    def index(self, packagename = None):
        """
        Entry point into the controller. Displays information about the package.

        ``packagename``
            Package name to look at.
        """
        package = self._get_package(packagename)

        c.session = session
        c.constants = constants
        c.outcomes = {
            _('Unreviewed') : constants.PACKAGE_COMMENT_OUTCOME_UNREVIEWED,
            _('Needs work') : constants.PACKAGE_COMMENT_OUTCOME_NEEDS_WORK,
            _('Perfect') : constants.PACKAGE_COMMENT_OUTCOME_PERFECT,
        }

        if 'user_id' in session:
            c.user = meta.session.query(User).filter_by(id=session['user_id']).one()
        else:
            c.user = None

        log.debug('Rendering page')
        return render('/package/index.mako')

    def rfs(self, packagename):
        """
        RFS boilerplate creation.

        ``packagename``
            Package name to look at.
        """
        package = self._get_package(packagename)

        log.debug('Rendering page')
        return render('/package/rfs.mako')

    def subscribe(self, packagename):
        """
        Package subscription.

        ``packagename``
            Package name to look at.
        """
        if 'user_id' not in session:
            log.debug('Requires authentication')
            session['path_before_login'] = request.path_info
            session.save()
            redirect(url('login'))

        package = self._get_package(packagename)

        query = meta.session.query(PackageSubscription).filter_by(
            package=packagename).filter_by(user_id=session['user_id'])
        subscription = query.first()

        validation = False
        if request.method == 'POST':
            # The form has been submitted.
            try:
                fields = form.validate(PackageSubscribeForm,
                                       user_id=session['user_id'])
            except Exception, e:
                log.error('Failed validation')
                validation = e
            if not validation:
                if subscription is None:
                    # There is no previous subscription.
                    if fields['level'] != -1:
                        log.debug('Creating new subscription on %s' % packagename)
                        subscribe = PackageSubscription(
                            package=packagename,
                            user_id=session['user_id'],
                            level=fields['level'])
                        meta.session.add(subscribe)
                else:
                    # There is a previous subscription.
                    if fields['level'] != -1:
                        log.debug('Changing previous subscription on %s' % packagename)
                        subscription.level = fields['level']
                    else:
                        log.debug('Deleting previous subscription on %s' % packagename)
                        meta.session.delete(subscription)
                meta.session.commit()
                redirect(url('package', packagename=packagename))

        c.subscriptions = [
            (-1, _('No subscription')),
            (constants.SUBSCRIPTION_LEVEL_UPLOADS,
             _('Package upload notifications only')),
            (constants.SUBSCRIPTION_LEVEL_COMMENTS,
             _('Package upload and comment notifications'))]

        if subscription is None:
            c.current_subscription = -1
        else:
            c.current_subscription = subscription.level

        log.debug('Rendering page')
        if validation:
            return form.htmlfill(render('/package/subscribe.mako'), validation)
        return render('/package/subscribe.mako')

    def delete(self, packagename):
        """
        Delete package.

        ``packagename``
            Package name to delete.
        """
        if 'user_id' not in session:
            log.debug('Requires authentication')
            session['path_before_login'] = request.path_info
            session.save()
            redirect(url('login'))

        # The user should have already been prompted with a nice dialog box
        # confirming their choice, so no mercy here.
        meta.session.delete(self._get_package(packagename))
        meta.session.commit()

        redirect(url(controller='packages', action='index', filter='my'))

    def comment(self, packagename):
        """
        Comment submission.

        ``packagename``
            Package name to look at.
        """
        if 'user_id' not in session:
            log.debug('Requires authentication')
            session['path_before_login'] = request.path_info
            session.save()
            redirect(url('login'))

        package = self._get_package(packagename)

        status = constants.PACKAGE_COMMENT_STATUS_NOT_UPLOADED
        try:
            fields = form.validate(PackageCommentForm)
        except Exception, e:
            log.error("failed validation")
            return form.htmlfill(self.index(packagename), e)

        if fields['status']:
            status = constants.PACKAGE_COMMENT_STATUS_UPLOADED

        comment = PackageComment(user_id=session['user_id'],
            package_version_id=fields['package_version'],
            text=fields['text'],
            time=datetime.now(),
            outcome=fields['outcome'],
            status=status)

        meta.session.add(comment)
        meta.session.commit()

        subscribers = meta.session.query(PackageSubscription).filter_by(
            package=packagename).filter(
            PackageSubscription.level <= constants.SUBSCRIPTION_LEVEL_COMMENTS).all()

        if len(subscribers) > 0:
            user = meta.session.query(User).filter_by(id=session['user_id']).one()

            email = Email('comment_posted')
            email.send([s.user.email for s in subscribers], package=packagename,
                comment=fields['text'], user=user)

        redirect(url('package', packagename=packagename))

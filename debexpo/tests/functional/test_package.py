# This needs to happen before the rest of the imports
from mock import Mock
import sys
sys.modules['debexpo.message'] = Mock()

from debexpo.tests import TestController, url
from debexpo.lib import constants
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.packages import Package
from debexpo.model.package_comments import PackageComment
from debexpo.model.package_versions import PackageVersion
from debexpo.model.source_packages import SourcePackage
from debexpo.model.package_subscriptions import PackageSubscription
from datetime import datetime

class TestPackageController(TestController):

    def setUp(self):
        self._setup_models()
        self._setup_example_user()
        user = meta.session.query(User).filter(
            User.email=='email@example.com').one()
        package = Package(name='testpackage', user=user,
                          description='a test package')
        meta.session.add(package)
        package_version = PackageVersion(package=package, version='1.0-1',
                                         maintainer='Test User <email@example.com>',
                                         section='Admin',
                                         distribution='unstable',
                                         qa_status=0,
                                         component='main',
                                         priority='optional',
                                         closes='',
                                         uploaded=datetime.now())
        meta.session.add(package_version)
        meta.session.add(SourcePackage(package_version=package_version))
        meta.session.commit()

    def tearDown(self):
        package = meta.session.query(Package).filter(
            Package.name=='testpackage').first()
        if package:
            package_versions = meta.session.query(PackageVersion).filter(
                PackageVersion.package==package).all()
            for vers in package_versions:
                meta.session.query(SourcePackage).filter(
                    SourcePackage.package_version==vers).delete()
                meta.session.delete(vers)
            meta.session.delete(package)
        meta.session.commit()
        self._remove_example_user()

    def test_index(self):
        response = self.app.get(url(controller='package', action='index'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url(controller='packages', action='index', packagename=None)))
        response = self.app.get(url(controller='package', action='index',
                                    packagename='notapackage'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url(controller='packages', action='index', packagename=None)))
        response = self.app.get(url(controller='package', action='index',
                                    packagename='testpackage'))
        self.assertEquals(response.status_int, 200)
        self.assertEquals(len(response.lxml.xpath(
                    '//a[@href="%s"]' % url(
                        'packages-uploader',
                        id='email@example.com'))), 1)
        response = self.app.post(url('login'), self._AUTHDATA)
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        response = self.app.get(url(controller='package', action='index',
                                    packagename='testpackage'))
        self.assertEquals(response.status_int, 200)
        self.assertEquals(len(response.lxml.xpath(
                    '//a[@href="%s"]' % url(
                        controller='package', action='delete',
                        packagename='testpackage', key = user.get_upload_key()))), 1)
        self.assertEquals(len(response.lxml.xpath(
                    '//form[@action="%s"]' % url(
                        controller='package', action='comment',
                        packagename='testpackage'))), 1)

    def test_subscribe(self):
        response = self.app.get(url(controller='package', action='subscribe',
                                    packagename='testpackage'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        self.assertEquals(response.session['path_before_login'], url(
                controller='package', action='subscribe',
                packagename='testpackage'))
        self.app.post(url('login'), self._AUTHDATA)
        response = self.app.get(url(controller='package', action='subscribe',
                                    packagename='testpackage'))
        self.assertEquals(response.status_int, 200)
        subscribeforms = response.lxml.xpath(
            '//form[@action="%s" and @method="post"]' % url(
                controller='package', action='subscribe',
                packagename='testpackage'))
        self.assertEquals(len(subscribeforms), 1)
        options = subscribeforms[0].xpath('*/select[@name="level"]/option')
        self.assertEquals(len(options), 3)
        for option in options:
            self.assertTrue(option.attrib['value'] in [
                    str(item) for item in (
                        -1, constants.SUBSCRIPTION_LEVEL_UPLOADS,
                         constants.SUBSCRIPTION_LEVEL_COMMENTS)])
        response = self.app.post(url(controller='package', action='subscribe',
                                     packagename='testpackage'))
        self.assertEquals(response.status_int, 200)
        self.assertEquals(
            len(response.lxml.xpath(
                    '//span[@class="error-message"]')), 2)
        response = self.app.post(url(controller='package', action='subscribe',
                                     packagename='testpackage'),
                                 {'level': constants.SUBSCRIPTION_LEVEL_UPLOADS,
                                  'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url('package', packagename='testpackage')))
        subs = meta.session.query(PackageSubscription).filter_by(
            package='testpackage').filter_by(
            user_id=response.session['user_id']).one()
        self.assertEquals(subs.level, constants.SUBSCRIPTION_LEVEL_UPLOADS)
        response = self.app.get(url(controller='package', action='subscribe',
                                    packagename='testpackage'))
        self.assertEquals(
            len(response.lxml.xpath(
                    '//option[@value="%d" and @selected="selected"]' %
                    constants.SUBSCRIPTION_LEVEL_UPLOADS)), 1)
        response = self.app.post(url(controller='package', action='subscribe',
                                     packagename='testpackage'),
                                 {'level': constants.SUBSCRIPTION_LEVEL_COMMENTS,
                                  'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url('package', packagename='testpackage')))
        subs = meta.session.query(PackageSubscription).filter_by(
            package='testpackage').filter_by(
            user_id=response.session['user_id']).one()
        self.assertEquals(subs.level, constants.SUBSCRIPTION_LEVEL_COMMENTS)
        response = self.app.post(url(controller='package', action='subscribe',
                                     packagename='testpackage'),
                                 {'level': -1,
                                  'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url('package', packagename='testpackage')))
        subs = meta.session.query(PackageSubscription).filter_by(
            package='testpackage').filter_by(
            user_id=response.session['user_id']).first()
        self.assertEquals(subs, None)

    def test_delete(self):
        self.app.post(url('login'), self._AUTHDATA)
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        response = self.app.get(url(controller='package', action='delete',
                                    packagename='testpackage', key = "INVALIDKEY"), expect_errors=True)
        self.assertEquals(response.status_int, 402)
        response = self.app.get(url(controller='package', action='delete',
                                    packagename='testpackage', key = user.get_upload_key()))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url(controller='packages', action='my')))
        package = meta.session.query(Package).filter(
            Package.name=='testpackage').first()
        self.assertEquals(package, None)

    def test_comment(self):
        response = self.app.get(url(controller='package', action='comment',
                                    packagename='testpackage'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url(controller='package', action='index',
                    packagename='testpackage')))
        self.app.post(url('login'), self._AUTHDATA)
        response = self.app.get(url(controller='package', action='comment',
                                    packagename='testpackage'))
        self.assertTrue(response.location.endswith(
                url(controller='package', action='index',
                    packagename='testpackage')))
        self.assertEquals(response.status_int, 302)
        response = self.app.post(
            url(controller='package', action='comment',
                packagename='testpackage'),
            {'package_version': 1,
             'text': 'This is a test comment',
             'outcome': constants.PACKAGE_COMMENT_OUTCOME_UNREVIEWED,
             'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url(controller='package', action='index',
                    packagename='testpackage')))
        comment = meta.session.query(PackageComment).filter_by(
            package_version_id=1).one()
        self.assertEquals(comment.text, 'This is a test comment')
        self.assertEquals(comment.status,
                          constants.PACKAGE_COMMENT_STATUS_NOT_UPLOADED)
        meta.session.delete(comment)
        # test with a subscriber
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        packsub = PackageSubscription(
            package='testpackage',
            level=constants.SUBSCRIPTION_LEVEL_COMMENTS)
        packsub.user = user
        meta.session.add(packsub)
        meta.session.commit()
        response = self.app.post(
            url(controller='package', action='comment',
                packagename='testpackage'),
            {'package_version': 1,
             'text': 'This is a test comment',
             'outcome': constants.PACKAGE_COMMENT_OUTCOME_UNREVIEWED,
             'commit': 'submit',
             'status': 'checked'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
                url(controller='package', action='index',
                    packagename='testpackage')))
        comment = meta.session.query(PackageComment).filter_by(
            package_version_id=1).one()
        self.assertEquals(comment.text, 'This is a test comment')
        self.assertEquals(comment.status,
                          constants.PACKAGE_COMMENT_STATUS_UPLOADED)
        meta.session.delete(packsub)
        meta.session.commit()

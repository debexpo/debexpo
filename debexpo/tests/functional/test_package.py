from debexpo.tests import TestController, url
from debexpo.lib import constants
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.packages import Package
from debexpo.model.package_comments import PackageComment
from debexpo.model.package_versions import PackageVersion
from debexpo.model.package_info import PackageInfo
from debexpo.model.package_subscriptions import PackageSubscription
from debexpo.controllers.package import PackageController
from datetime import datetime
import pylons.test
import md5


class TestPackageController(TestController):

    def setUp(self):
        self._setup_models()
        self._setup_example_user()
        self._setup_example_package()

    def tearDown(self):
        self._remove_example_package()
        self._remove_example_user()

    def _test_no_auth(self, action, redirect_login=True):
        user = meta.session.query(User).filter(
            User.email == 'email@example.com').one()
        response = self.app.get(url(
            controller='package', action=action, packagename='testpackage',
            key=user.get_upload_key()))
        self.assertEquals(response.status_int, 302)
        if (redirect_login):
            self.assertTrue(response.location.endswith(url('login')))

    def _test_wrong_key(self, action):
        self.app.post(url('login'), self._AUTHDATA)
        response = self.app.get(url(
            controller='package', action=action, packagename='testpackage',
            key='wrong'), expect_errors=True)
        self.assertEquals(response.status_int, 402)

    def _test_not_owned_package(self, action):
        user = User(name='Another user', email='another@example.com',
                    password=md5.new('password').hexdigest(),
                    lastlogin=datetime.now())
        meta.session.add(user)
        meta.session.commit()
        self.app.post(url('login'), {'email': 'another@example.com',
                                     'password': 'password',
                                     'commit': 'submit'})
        user = meta.session.query(User).filter(
            User.email == 'another@example.com').one()
        response = self.app.get(url(
            controller='package', action=action, packagename='testpackage',
            key=user.get_upload_key()), expect_errors=True)
        self.assertEquals(response.status_int, 403)
        meta.session.delete(user)

    def test_index(self):
        user = meta.session.query(User).filter(
            User.email == 'email@example.com').one()
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
            '//a[@href="%s"]' % url(controller='packages',
                                    action='uploader',
                                    id='email@example.com'))), 1)
        response = self.app.post(url('login'), self._AUTHDATA)
        response = self.app.get(url(controller='package', action='index',
                                    packagename='testpackage'))
        self.assertEquals(response.status_int, 200)
        self.assertEquals(len(response.lxml.xpath(
            '//a[@href="%s"]' % url(
                controller='package', action='delete',
                packagename='testpackage',
                key=user.get_upload_key()))), 1)
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
        response = self.app.post(url(controller='package',
                                     action='subscribe',
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
        response = self.app.post(
                url(controller='package',
                    action='subscribe',
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

    def test_get_package_from_crontab_wrong_package(self):
        pkg_controller = PackageController()
        package = pkg_controller._get_package('nonexistant',
                                              from_controller=False)
        self.assertEquals(package, None)

    def test_get_package_from_crontab(self):
        pkg_controller = PackageController()
        package = pkg_controller._get_package('testpackage',
                                              from_controller=False)
        self.assertEquals(package.name, 'testpackage')

    def test_delete_no_auth(self):
        self._test_no_auth('delete')

    def test_delete_not_owned_package(self):
        self._test_not_owned_package('delete')

    def test_delete_wrong_key(self):
        self._test_wrong_key('delete')

    def test_delete_successful(self):
        self.app.post(url('login'), self._AUTHDATA)
        user = meta.session.query(User).filter(
            User.email == 'email@example.com').one()
        response = self.app.get(url(
            controller='package', action='delete', packagename='testpackage',
            key=user.get_upload_key()))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
            url(controller='packages', action='my')))
        package = meta.session.query(Package).filter(
            Package.name == 'testpackage').first()
        self.assertEquals(package, None)

    def test_comment_show(self):
        response = self.app.get(
            url(controller='package', action='comment',
                packagename='testpackage'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(
            url(controller='package', action='index',
                packagename='testpackage')))

    def test_comment_no_auth(self):
        response = self.app.post(
            url(controller='package', action='comment',
                packagename='testpackage'),
            {'package_version': 1,
             'text': 'This is a test comment',
             'outcome': constants.PACKAGE_COMMENT_OUTCOME_UNREVIEWED,
             'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))

    def test_comment(self):
        self.app.post(url('login'), self._AUTHDATA)
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

    def test_comment_with_subscriber(self):
        # test with a subscriber
        pylons.test.pylonsapp.config['debexpo.testsmtp'] = '/tmp/debexpo.msg'
        self.app.post(url('login'), self._AUTHDATA)
        user = meta.session.query(User).filter(
            User.email == 'email@example.com').one()
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

    def test_sponsor_no_auth(self):
        self._test_no_auth('sponsor')

    def test_sponsor_wrong_key(self):
        self._test_wrong_key('sponsor')

    def test_sponsor_not_owned_package(self):
        self._test_not_owned_package('sponsor')

    def test_sponsor_toggle(self, toggle=True):
        self.app.post(url('login'), self._AUTHDATA)
        user = meta.session.query(User).filter(
            User.email == 'email@example.com').one()
        response = self.app.get(url(
            controller='package', action='sponsor', packagename='testpackage',
            key=user.get_upload_key()))
        self.assertEquals(response.status_int, 302)
        package = meta.session.query(Package).filter(
            Package.name == 'testpackage').first()
        if (toggle):
            self.assertFalse(package.needs_sponsor)
            self.test_sponsor_toggle(toggle=False)
        else:
            self.assertTrue(package.needs_sponsor)

    def test_package_info_rich_data(self):
        package = meta.session.query(Package).filter(
            Package.name == 'testpackage').first()
        package_version = meta.session.query(PackageVersion).filter(
            PackageVersion.package == package).first()
        textmark = 'some lintian output'
        package_info_data = PackageInfo(
            package_version_id=package_version.id,
            from_plugin='LintianPlugin',
            outcome='Package is lintian clean',
            rich_data=textmark,
            severity=constants.PLUGIN_SEVERITY_INFO)
        meta.session.add(package_info_data)
        meta.session.commit()
        response = self.app.get(url(controller='package', action='index',
                                    packagename='testpackage'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue(textmark in response)

    def test_package_info_data(self):
        package = meta.session.query(Package).filter(
            Package.name == 'testpackage').first()
        package_version = meta.session.query(PackageVersion).filter(
            PackageVersion.package == package).first()
        textmark = 'some lintian output'
        package_info_data = PackageInfo(
            package_version_id=package_version.id,
            from_plugin='LintianPlugin',
            outcome='Package is lintian clean',
            data=textmark,
            severity=constants.PLUGIN_SEVERITY_INFO)
        meta.session.add(package_info_data)
        meta.session.commit()
        response = self.app.get(url(controller='package', action='index',
                                    packagename='testpackage'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue(textmark in response)

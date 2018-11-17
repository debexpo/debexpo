from debexpo.tests import *
from debexpo.lib.constants import PACKAGE_NEEDS_SPONSOR_YES
from debexpo.model import meta
from debexpo.model.packages import Package

class TestPackagesController(TestController):

    def setUp(self):
        self._setup_models()
        self._setup_example_user()
        self._setup_example_package()

    def tearDown(self):
        self._remove_example_package()
        self._remove_example_user()

    def _test_feed_filter(self, filter=None, id=None):
        response = self.app.get(url(controller='packages', action='feed',
                                    filter=filter, id=id))
        self.assertEquals(200, response.status_int)
        self.assertEquals('application/rss+xml', response.content_type)
        self.assertTrue('<title>testpackage 1.0-1</title>' in response.body)
        return response

    def test_index(self):
        response = self.app.get(url(controller='packages', action='index'))
        self.assertEquals(200, response.status_int)
        self.assertEquals('text/html', response.content_type)

    def test_feed(self):
        self._test_feed_filter()

    def test_feed_with_sponsor(self):
        package = meta.session.query(
                Package).filter(Package.name == 'testpackage').first()
        package.needs_sponsor = PACKAGE_NEEDS_SPONSOR_YES
        meta.session.commit()
        response = self._test_feed_filter()
        self.assertTrue('Uploader is currently looking for a sponsor.' in response.body)

    def test_feed_section(self):
        self._test_feed_filter('section', 'Admin')

    def test_feed_uploader(self):
        self._test_feed_filter('uploader', 'email@example.com')

    def test_feed_wrong_uploader(self):
        response = self.app.get(url(controller='packages', action='feed',
                                    filter='uploader',
                                    id='nonexistent@example.com'))
        self.assertEquals(200, response.status_int)
        self.assertEquals('application/rss+xml', response.content_type)
        self.assertTrue('<title>testpackage 1.0-1</title>' not in response.body)

    def test_feed_maintainer(self):
        self._test_feed_filter('maintainer', 'Test User <email@example.com>')

    def test_section(self):
        response = self.app.get(url(controller='packages', action='section', id='main'))
        self.assertEquals(200, response.status_int)
        self.assertEquals('text/html', response.content_type)

    def test_uploader(self):
        response = self.app.get(url('packages-uploader', id='nonexistant@example.com'), expect_errors = True)
        self.assertEquals(404, response.status_int)
        response = self.app.get(url('packages-uploader', id='email@example.com'))
        self.assertEquals(200, response.status_int)
        self.assertEquals('text/html', response.content_type)


    def test_my(self):
        response = self.app.get(url(controller='packages', action='my'))
        self.assertEquals(302, response.status_int)
        self.assertTrue(response.location.endswith(url('login')))

    def test_maintainer(self):
        response = self.app.get(url(controller='packages', action='maintainer', id='Test'))
        self.assertEquals(200, response.status_int)
        self.assertEquals('text/html', response.content_type)

from debexpo.tests import *

class TestPackagesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='packages', action='index'))
        self.assertEquals(200, response.status_int)
        self.assertEquals('text/html', response.content_type)

    def test_feed(self):
        response = self.app.get(url(controller='packages', action='feed'))
        self.assertEquals(200, response.status_int)
        self.assertEquals('application/rss+xml', response.content_type)

    def test_section(self):
        response = self.app.get(url(controller='packages', action='section', id='main'))
        self.assertEquals(200, response.status_int)
        self.assertEquals('text/html', response.content_type)

    def test_uploader(self):
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

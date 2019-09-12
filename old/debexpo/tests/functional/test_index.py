from debexpo.tests import TestController
from pylons import url
import pylons.test


class TestIndexController(TestController):
    def test_index(self):
        # test a normal index page
        testurl = url(controller='index', action='index')
        pylons.test.pylonsapp.config['debexpo.sitename'] = 'test index'
        response = self.app.get(testurl)
        testtext = '<h1>Welcome to test index</h1>'
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

    def test_contact(self):
        response = self.app.get(url(controller='index', action='contact'))
        testtext = '<h1>Site contact</h1>'
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

    def test_qa(self):
        response = self.app.get(url(controller='index', action='qa'))
        testtext = '<h1>Questions &amp; Answers</h1>'
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

    def test_intro_reviewer(self):
        response = self.app.get(url(controller='index',
                                    action='intro-reviewers'))
        testtext = '<h1>Package reviews</h1>'
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

    def test_intro_maintainers(self):
        response = self.app.get(url(controller='index',
                                    action='intro-maintainers'))
        testtext = "{}".format('<h1>Introduction for maintainers: How will my',
                               ' package get into Debian</h1>')
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

    def test_intro_sponsors(self):
        testurl = url('sponsors')
        response = self.app.get(testurl)
        testtext = '<h1>The sponsoring process</h1>'
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

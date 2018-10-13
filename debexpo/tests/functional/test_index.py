from debexpo.tests import TestController
from pylons import url
from tempfile import mkdtemp
from shutil import rmtree
import os
import os.path
import pylons.test


class TestIndexController(TestController):
    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        rmtree(self.tempdir)

    def _generate_temppage(self, filename, text):
        temppage = os.path.join(self.tempdir, filename)
        f = open(temppage, 'w')
        f.write(text)
        f.close()
        return temppage

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
        self.assertEquals(response.status_int, 200)

    def test_intro_maintainers(self):
        testurl = url('intro-maintainers')
        response = self.app.get(testurl)
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

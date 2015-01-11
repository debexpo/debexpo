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
        response = self.app.get(testurl)
        self.assertEquals(response.status_int, 200)

        testtext = '<title>mentors.debian.net</title>'
        pylons.test.pylonsapp.config['debexpo.html.frontpage'] = \
            self._generate_temppage('front.html', testtext)

        response = self.app.get(testurl)
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

        del pylons.test.pylonsapp.config['debexpo.html.frontpage']

    def test_contact(self):
        response = self.app.get(url(controller='index', action='contact'))
        self.assertEquals(response.status_int, 200)

    def test_intro_maintainers(self):
        testurl = url('intro-maintainers')
        response = self.app.get(testurl)
        self.assertEquals(response.status_int, 200)

        testtext = '<h1>Introduction for maintainers: How will my package get into Debian</h1>'
        pylons.test.pylonsapp.config['debexpo.html.maintainer_intro'] = \
            self._generate_temppage('maintainer_intro.html', testtext)

        response = self.app.get(testurl)
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

        del pylons.test.pylonsapp.config['debexpo.html.maintainer_intro']

    def test_intro_sponsors(self):
        testurl = url('sponsors')
        response = self.app.get(testurl)
        self.assertEquals(response.status_int, 200)

        testtext = '<h1>The sponsoring process</h1>'
        pylons.test.pylonsapp.config['debexpo.html.sponsors_intro'] = \
            self._generate_temppage('sponsor_intro.html', testtext)

        response = self.app.get(testurl)
        self.assertEquals(response.status_int, 200)
        self.assertTrue(testtext in response)

        del pylons.test.pylonsapp.config['debexpo.html.sponsors_intro']

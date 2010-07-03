from debexpo.tests import TestController, url
from debexpo.lib import constants
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.user_countries import UserCountry
import md5

class TestMyController(TestController):
    _GPGKEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.10 (GNU/Linux)

mQENBEwmV4wBCADCbdBf65H0r13XfVVncCc9pW7XkDYuKD8locXY48IdKVQRKK97
lJUZv7Ys/nx1QTTux/S7ldhQS2Op4pA86uEQOnynmM2S5uePIslbkRKGnfcfUYdE
9Ij7S0+ZIafr2MUdehFLuPhCH9ddepA5rSLfgVfMAUpwyZ+/VZOCxczLntOWhTqH
xcN4aHJ7M6EXixH4uOe+hL2PeNw1LGN/ESXgEsPuJkYnKQb6XYFGFb08WyiJ7AXZ
JMuajajTw626U2rsqoi4HNHFifGm3K2+htR5V9gStdF7CxmCAgGyQ+/vhqMAv6zv
HLWWLbSIUOftAT6zHcu/DI9yWESe1WH6hayBABEBAAG0HVRlc3QgdXNlciA8ZW1h
aWxAZXhhbXBsZS5jb20+iQE4BBMBAgAiBQJMJleMAhsDBgsJCAcDAgYVCAIJCgsE
FgIDAQIeAQIXgAAKCRAKG4hEZ1gmHq1kCACOmW8SuVYSDIhAHWmlA9Ch4QIPsCMt
9FazOHN72Gr1gB8rdUJ0qGzkOiP349sjSPqVfHz9NX830ng2QvFl0hiVCdtUlERn
ijgBUGu0nPIpZH0UskWVXthndL3twmGtfIxwzsZEWeOrmRg24q4PMBqIOA1SNowk
Ck14LkmR65Ds9a/KS23Mnd5YoH+NDB5fABXU0vgdn6il9tJhYYJPSvssj0AoF620
h9VAJ+/qpCNxmIZBa6NhDcyOoFg0i5nPo4qJRx7e1KmApGjFdW9c/Rz8pBD3v5iQ
dfkC6NRhQVoWMzVPv7RiDuC0Ig7ub1QZ8waSNDW2uwLLqwM9bRNmedY2uQENBEwm
V4wBCACw8DO6P7tVTaYlhqffAPMpJE6O9yjqz+3LDJCXJhPD+js8y5P/6i8QA80K
F2jXpphp+d/iqMbIpp+p2w2OpoF6mbc/Frf3Jjx+4pL5lwWzoicdGvxdjDeXYmCc
zI9AxderVEh4sokN9B6i/1dG9EOpkkbQ+gt9xP1Wbc4oi+03TvjEA1s+nToEkSgy
dk2Xg69IgRBGyP8+x/Yzi5pWZrfGES0/Ui6+hfiJY6fYcLnW3mWFuJ9DZdx0JRmY
mKqzorfmnHqYkUcJEKBSP6NjS2A3+SfCyZYBCFkDOZFY1zp7YtDkMTV4/vvSXBdt
/oZNVztZk8C2n9TQve4My6kPoWfzABEBAAGJAR8EGAECAAkFAkwmV4wCGwwACgkQ
ChuIRGdYJh64QQf+KXt6/VqrjYymGvKtOdufepJpBIoUehztZxJ+QSe+eL4ttrme
BPtS964reKahaP8K77rowdBtEdOCXhFc5wLSHTNqsLB2lC3y3pzEotfxa2pyO7jG
2Boy8TIj5a6ixA1nwEwPgX6RkZwnGCn17wQzTV8y8OV8ei7z/so6VHkndRVOt9O+
x7HPR7QKPp2p/JtwP6xJUtZgaDKvBpK4rISqv7MiSHljIa4sq7wfdHw8zJ8ZTtYv
2USGdIn3QtoVRN+fsGzs2rRWK6Cc1AgNqhLgna+qagAq9hB3u52G9tjAlx2MD7yD
ABRL0EeYuGCJYJRQsw8e8JuRSaVGwfotqkIHtQ==
=PXiv
-----END PGP PUBLIC KEY BLOCK-----
"""
    _GPG_ID = '2048R/6758261E'

    def setUp(self):
        self._setup_models()
        self._setup_example_user()
        self._setup_example_countries()

    def tearDown(self):
        self._remove_example_user()
        self._remove_example_countries()

    def test_index(self):
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        self.assertEquals(response.session['path_before_login'], url('my'))
        response = self.app.post(url('login'), self._AUTHDATA)
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % (url('logout')) in response)

        # test user with country
        user = meta.session.query(User).filter(
            User.email=='email@example.com').one()
        user.country = meta.session.query(UserCountry).filter(
            UserCountry.name=='Germany').one()
        meta.session.commit()
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % (url('logout')) in response)

        # test DD user
        user = meta.session.query(User).filter(
            User.email=='email@example.com').one()
        user.status = constants.USER_STATUS_DEVELOPER
        meta.session.commit()
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % (url('logout')) in response)

        # test DM user
        user = meta.session.query(User).filter(
            User.email=='email@example.com').one()
        user.status = constants.USER_STATUS_MAINTAINER
        meta.session.commit()
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % (url('logout')) in response)

        # test handling of deleted user
        self._remove_example_user()
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))

    def test__gpg(self):
        response = self.app.post(url('my'), {'form': 'gpg'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url('login'), self._AUTHDATA)
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        self.assertEquals(user.gpg, None)

        # upload GPG key
        response = self.app.post(url('my'), {'form': 'gpg',
                                             'delete_gpg': 0,
                                             'commit': 'submit'},
                                 upload_files = [('gpg', 'mykey.asc',
                                                  self._GPGKEY)])
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        self.assertEquals(user.gpg, self._GPGKEY)

        # test whether index page contains GPG delete link
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % (url('logout')) in response)
        self.assertTrue(self._GPG_ID in response)

        # delete GPG key
        response = self.app.post(url('my'), {'form': 'gpg',
                                             'delete_gpg': 1,
                                             'commit': 'submit',
                                             'gpg': ''})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        self.assertEquals(user.gpg, None)

    def test__details(self):
        response = self.app.post(url('my'), {'form': 'details'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url('login'), self._AUTHDATA)
        response = self.app.post(url('my'), {'form': 'details',
                                             'name': '',
                                             'email': 'email2@example.com',
                                             'commit': 'submit'})
        self.assertEquals(response.status_int, 200)
        self.assertEquals(len(response.lxml.xpath('//input[@id="name" and @class="error"]')),
                          1)
        response = self.app.post(url('my'), {'form': 'details',
                                             'name': 'Test user2',
                                             'email': 'email2@example.com',
                                             'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User).filter(User.email=='email@example.com').first()
        self.assertEquals(user, None)
        user = meta.session.query(User).filter(User.email=='email2@example.com').one()
        self.assertEquals(user.name, 'Test user2')
        meta.session.delete(user)
        meta.session.commit()

    def test__password(self):
        response = self.app.post(url('my'), {'form': 'password'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url('login'), self._AUTHDATA)
        response = self.app.post(url('my'), {'form': 'password',
                                             'password_current': 'password',
                                             'password_new': 'newpassword',
                                             'password_confirm': 'newpassword',
                                             'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User).filter(
            User.email=='email@example.com').filter(
            User.password==md5.new('newpassword').hexdigest()).one()
        self.assertEquals(user.name, 'Test user')

    def test__other_details(self):
        response = self.app.post(url('my'), {'form': 'other_details'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url('login'), self._AUTHDATA)
        # test set ircnick
        response = self.app.post(url('my'), {'form': 'other_details',
                                             'country': '',
                                             'ircnick': 'tester',
                                             'jabber': '',
                                             'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        self.assertEquals(user.ircnick, 'tester')
        # test DM switch
        response = self.app.post(url('my'), {'form': 'other_details',
                                             'country': -1,
                                             'ircnick': 'tester',
                                             'jabber': '',
                                             'status': 1,
                                             'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        self.assertEquals(user.status, constants.USER_STATUS_MAINTAINER)

    def test__invalid_form(self):
        response = self.app.post(url('my'), {'form': 'invalid'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url('login'), self._AUTHDATA)
        response = self.app.post(url('my'), {'form': 'invalid'})
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % url('logout') in response)

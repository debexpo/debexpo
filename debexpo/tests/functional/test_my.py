from debexpo.tests import TestController, url
from debexpo.lib import constants
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.user_countries import UserCountry
import md5

class TestMyController(TestController):
    _LOW_STRENGTH_GPGKEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
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
    _LOW_STRENGTH_GPG_ID = '2048R/6758261E'

    _HIGH_STRENGTH_GPGKEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.12 (GNU/Linux)

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
=fw7J
-----END PGP PUBLIC KEY BLOCK-----
"""

    _HIGH_STRENGTH_GPG_ID = '4096R/AC4ABA99'

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

        # upload GPG key with low strength
        response = self.app.post(url('my'), {'form': 'gpg',
                                             'delete_gpg': 0,
                                             'commit': 'submit'},
                                 upload_files = [('gpg', 'mykey.asc',
                                                  self._LOW_STRENGTH_GPGKEY)])
        self.assertEquals(response.status_int, 200)
        low_strength_msg = 'Key strength unacceptable in Debian Keyring. The minimum required key strength is'
        self.assertTrue(low_strength_msg in response)
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        self.assertEquals(user.gpg, None)

        # upload GPG key with high strength
        response = self.app.post(url('my'), {'form': 'gpg',
                                             'delete_gpg': 0,
                                             'commit': 'submit'},
                                 upload_files = [('gpg', 'mykey.asc',
                                                  self._HIGH_STRENGTH_GPGKEY)])
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User).filter(User.email=='email@example.com').one()
        self.assertEquals(user.gpg, self._HIGH_STRENGTH_GPGKEY)

        # test whether index page contains GPG delete link
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % (url('logout')) in response)
        self.assertTrue(self._HIGH_STRENGTH_GPG_ID in response)

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

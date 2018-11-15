from debexpo.tests import TestController, url
from debexpo.lib import constants
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.user_countries import UserCountry
import md5
import tempfile
import os
import shutil

class TestMyController(TestController):
    _GPGKEY_WRONG_EMAIL = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEW9b91RYJKwYBBAHaRw8BAQdAHtUIQWAsmPilu0JDMnLbpPQfT1i3z2IVMoDH
rhlYkO+0JWRlYmV4cG8gdGVzdGluZyA8ZGViZXhwb0BleGFtcGxlLm9yZz6IkAQT
FggAOBYhBOF57qTrR+YF2YZjLihiGOfHT5wRBQJb1v3VAhsDBQsJCAcCBhUKCQgL
AgQWAgMBAh4BAheAAAoJEChiGOfHT5wRdQIBAJ8rciR0e1PaA+LhoTWHaPSgCwvc
lNFyRk71s75+hRkhAPwPnl6QqGsOa0DyJB5saVcqPCqYFbF1usUWIQnPPRsVC7g4
BFvW/dUSCisGAQQBl1UBBQEBB0DzrYDCp+OaNFinqKkDWcqftqq/BAFS9lq4de5g
RNytNAMBCAeIeAQYFggAIBYhBOF57qTrR+YF2YZjLihiGOfHT5wRBQJb1v3VAhsM
AAoJEChiGOfHT5wRNK8A/115pc8+OwKDy1fGXGX3l0uq1wdfiJreG/9YZddx/JTI
AQD4ZLpyUg+z6kJ+8YAmHFiOD9Ixv3QVvrfpBwnBVtJZBg==
=N+9W
-----END PGP PUBLIC KEY BLOCK-----"""

    _GPG_ID_WRONG_EMAIL = '256E/C74F9C11'

    _GPGKEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEW+iERRYJKwYBBAHaRw8BAQdAZN+9IfILcMWaZ5bOx4Ykmum/1ZMaxZAw1YbI
KjEWWU60J0RlYmV4cG8gdGVzdGluZyBrZXkgPGVtYWlsQGV4YW1wbGUuY29tPoiQ
BBMWCAA4FiEEdhj55Cj1+6e2+jO1NU98o/QgaL4FAlvohEUCGwMFCwkIBwIGFQoJ
CAsCBBYCAwECHgECF4AACgkQNU98o/QgaL7I+wEAjY6np4hgEfkotEM0hpOo1LGF
sWWiO1OKhi/Nfg+WOoUA/0/DEcGfclpGhpB+unaqn0dLnMKDJeZAxINji7/Lz2gH
uDgEW+iERRIKKwYBBAGXVQEFAQEHQJwX6mLJZQMkBwKbyJa0+oz15wSiYHFONGYI
s9TdseYWAwEIB4h4BBgWCAAgFiEEdhj55Cj1+6e2+jO1NU98o/QgaL4FAlvohEUC
GwwACgkQNU98o/QgaL6XtAEAl+8Pqc8q6EWTudqgynVIpdraSuBrVSaEcxffKaT3
P6YA/0SM1Yi/F2maISv8k44MzRAdGf2yFabwsfdCH+RLD6YO
=BYiE
-----END PGP PUBLIC KEY BLOCK-----"""
    _GPG_ID= '256E/F42068BE'

    def _setup_gpg_env(self):
        self.homedir = tempfile.mkdtemp()
        os.environ['GNUPGHOME'] = self.homedir

    def _cleanup_gpg_env(self):
        shutil.rmtree(self.homedir)

    def setUp(self):
        self._setup_gpg_env()
        self._setup_models()
        self._setup_example_user()
        self._setup_example_countries()

    def tearDown(self):
        self._remove_example_user()
        self._remove_example_countries()
        self._cleanup_gpg_env()

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

    def test__gpg_wrong_email(self):
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
                                                  self._GPGKEY_WRONG_EMAIL)])
        self.assertEquals(response.status_int, 200)
        self.assertTrue('None of your user IDs in key {} does match your'
                        ' profile mail address'.format(self._GPG_ID_WRONG_EMAIL)
                        in response)
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

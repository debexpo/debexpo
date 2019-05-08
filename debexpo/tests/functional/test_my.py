from debexpo.tests import TestController, url
from debexpo.lib import constants
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.model.user_countries import UserCountry

import tempfile
import os
import shutil

from passlib.hash import bcrypt


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

    _GPGKEY_MULTI = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEXLTbcxYJKwYBBAHaRw8BAQdAoh3VCQpeRnjWSsGxL8TmOE6AOc5W/3BGt+TH
NlTNv2e0LVZpbmNlbnQgVElNRSAoVEVTVElORyBLRVkgMSkgPHZ0aW1lQGNpbGcu
b3JnPoiQBBMWCAA4FiEE2QTvCDJA2cJrCuaBNkkwohbvF/0FAly023MCGwMFCwkI
BwIGFQoJCAsCBBYCAwECHgECF4AACgkQNkkwohbvF/24QgEAhjlLjQzHSR7xR4+I
i0KVuRBw9gTiLGN80UVt8s0ONGEA/3Ft1HQ5b37rFSY44Yvnuv8ejdTMqhO0sZ0J
3OKTuVcBuDgEXLTbcxIKKwYBBAGXVQEFAQEHQBQ1AKhzJ+miI9wlpeTPfKzbYPIb
fN3+uHMNRAsP0zoaAwEIB4h4BBgWCAAgFiEE2QTvCDJA2cJrCuaBNkkwohbvF/0F
Aly023MCGwwACgkQNkkwohbvF/0hGAEAxkUFu5BAKwEToaoLs/0sePvL0S+EnR7F
b0uzAD7qCN0BAKEKKL6PoMD5cwSlaN1j6z3K5UbPvkMulGXK38vt110LmDMEXLTb
lxYJKwYBBAHaRw8BAQdA0nglRFeDWhHZq7a9UfIjLyupPutx9DL7+qk+Wfml0Uy0
LVZpbmNlbnQgVElNRSAoVEVTVElORyBLRVkgMikgPHZ0aW1lQGNpbGcub3JnPoiQ
BBMWCAA4FiEEdLUyC8hsXaia62wnbaTvWsnriSoFAly025cCGwMFCwkIBwIGFQoJ
CAsCBBYCAwECHgECF4AACgkQbaTvWsnriSpQCwEA5sJ8Bfm1BMwhMZet53o5k74t
X6P/piUOFeifO/c6tQ0A/33bE2W/7m9S8SJzcsin9ISEOSV2Z2dPQhCPj8afu+EC
uDgEXLTblxIKKwYBBAGXVQEFAQEHQPuCyECR7wFvp1wKwzBMK/bBMi/UFxeh0qoZ
GdQ6ChBXAwEIB4h4BBgWCAAgFiEEdLUyC8hsXaia62wnbaTvWsnriSoFAly025cC
GwwACgkQbaTvWsnriSqzewD+JDfQwbYmNVzshxGGHslGO9yx3WShsdQUxZgs4HeD
qd4BAMRseQ8Lg7Np6xDdqm4m2YaNhQmebe3pnwN81514V20J
=gMOI
-----END PGP PUBLIC KEY BLOCK-----"""

    _GPG_ID_WRONG_EMAIL = '256E/C74F9C11'

    _GPGKEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEW/GBqhYJKwYBBAHaRw8BAQdA+6hBA4PcdcPwgMsKGQXrqwbJemLBgS1PkKZg
RFlKdKi0IHByaW1hcnkgaWQgPHByaW1hcnlAZXhhbXBsZS5vcmc+iJMEExYIADsC
GwMFCwkIBwIGFQoJCAsCBBYCAwECHgECF4AWIQRVkwbu4cjBst0cc7HENHgc6HHz
3wUCW/GB7AIZAQAKCRDENHgc6HHz35EOAP9lXBb8lm72xPeMdjRL+TU83PimD0NZ
urQfnnLVZOu4tAEAqdrz/2q41mScnKJFAnQ5pan5FYlUnDR2WVp1kiFoPwu0HVRl
c3QgdXNlciA8ZW1haWxAZXhhbXBsZS5jb20+iJAEExYIADgWIQRVkwbu4cjBst0c
c7HENHgc6HHz3wUCW/GB6AIbAwULCQgHAgYVCgkICwIEFgIDAQIeAQIXgAAKCRDE
NHgc6HHz3yr6AP9MyMaz+dsOC3R/WnjE8EdM42mpf3VkKY0icS60K/Aj3QD/XkIA
qs+ItQAUoeqZM3jh0HvLwUESxm6FtCltwyGlqwW4OARb8YGqEgorBgEEAZdVAQUB
AQdANrk3qq/eP1TEWfFZqhR0vcz7YB9c5+OnvMV+xO4W3nQDAQgHiHgEGBYIACAW
IQRVkwbu4cjBst0cc7HENHgc6HHz3wUCW/GBqgIbDAAKCRDENHgc6HHz3/CHAP0c
hxes4Ebtg7N8B/BoMYwmUVvmMVmoV+ef/vqYvfm6sgEA6fKzMSXllw57UJ90Unyn
xOwJ1heEnfmgPkuiz7jFCAo=
=xgUN
-----END PGP PUBLIC KEY BLOCK-----"""
    _GPG_ID = '256E/E871F3DF'

    def _setup_gpg_env(self):
        self.homedir = tempfile.mkdtemp()
        os.environ['GNUPGHOME'] = self.homedir

    def _cleanup_gpg_env(self):
        os.unsetenv('GNUPGHOME')
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
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        user.country = meta.session.query(UserCountry) \
            .filter(UserCountry.name == 'Germany') \
            .one()
        meta.session.commit()
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % (url('logout')) in response)

        # test DD user
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        user.status = constants.USER_STATUS_DEVELOPER
        meta.session.commit()
        response = self.app.get(url(controller='my', action='index'))
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % (url('logout')) in response)

        # test DM user
        user = meta.session.query(User).filter(
            User.email == 'email@example.com').one()
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
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        self.assertEquals(user.gpg, None)

        # upload GPG key
        response = self.app.post(url('my'), {'form': 'gpg',
                                             'delete_gpg': 0,
                                             'commit': 'submit'},
                                 upload_files=[('gpg', 'mykey.asc',
                                               self._GPGKEY)])
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
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
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        self.assertEquals(user.gpg, None)

    def test__gpg_multi_keys(self):
        response = self.app.post(url('my'), {'form': 'gpg'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url('login'), self._AUTHDATA)
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        self.assertEquals(user.gpg, None)

        # upload GPG key
        response = self.app.post(url('my'), {'form': 'gpg',
                                             'delete_gpg': 0,
                                             'commit': 'submit'},
                                 upload_files=[('gpg', 'mykey.asc',
                                               self._GPGKEY_MULTI)])
        self.assertEquals(response.status_int, 200)
        self.assertTrue('Multiple keys not supported' in response)
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        self.assertEquals(user.gpg, None)

    def test__gpg_wrong_email(self):
        response = self.app.post(url('my'), {'form': 'gpg'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url('login'), self._AUTHDATA)
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        self.assertEquals(user.gpg, None)

        # upload GPG key
        response = self.app.post(url('my'), {'form': 'gpg',
                                             'delete_gpg': 0,
                                             'commit': 'submit'},
                                 upload_files=[('gpg', 'mykey.asc',
                                               self._GPGKEY_WRONG_EMAIL)])
        self.assertEquals(response.status_int, 200)
        self.assertTrue('None of your user IDs in key {} does match your'
                        ' profile mail address'.format(self._GPG_ID_WRONG_EMAIL)
                        in response)
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
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
        self.assertEquals(len(response.lxml.xpath(
            '//input[@id="name" and @class="error"]')), 1)
        response = self.app.post(url('my'), {'form': 'details',
                                             'name': 'Test user2',
                                             'email': 'email2@example.com',
                                             'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .first()
        self.assertEquals(user, None)
        user = meta.session.query(User) \
            .filter(User.email == 'email2@example.com') \
            .one()
        self.assertEquals(user.name, 'Test user2')
        meta.session.delete(user)
        meta.session.commit()

    def test__password(self):
        response = self.app.post(url('my'), {'form': 'password'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))

        # Before first login, password is stored as md5
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        self.assertFalse(user.password.startswith('$2'))

        # Login
        response = self.app.post(url('login'), self._AUTHDATA)

        # Password updated with bcrypt
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        self.assertTrue(bcrypt.verify('password', user.password))

        # Test password change
        response = self.app.post(url('my'), {'form': 'password',
                                             'password_current': 'password',
                                             'password_new': 'newpassword',
                                             'password_confirm': 'newpassword',
                                             'commit': 'submit'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))

        # Test new password value
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
        self.assertTrue(bcrypt.verify('newpassword', user.password))

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
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .one()
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
        user = meta.session.query(User) \
            .filter(User.email == 'email@example.com')\
            .one()
        self.assertEquals(user.status, constants.USER_STATUS_MAINTAINER)

    def test__invalid_form(self):
        response = self.app.post(url('my'), {'form': 'invalid'})
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url('login'), self._AUTHDATA)
        response = self.app.post(url('my'), {'form': 'invalid'})
        self.assertEquals(response.status_int, 200)
        self.assertTrue('<a href="%s">' % url('logout') in response)

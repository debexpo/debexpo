#   test_profile.py - Functional tests for the profile page
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

from tests import TestController
from django.urls import reverse
# from debexpo.lib import constants
# from debexpo.model import meta
from debexpo.accounts.models import Countries, User, UserStatus
# from debexpo.model.user_countries import UserCountry
#
# import tempfile
# import os
# import shutil
#
# from passlib.hash import bcrypt
import logging

log = logging.getLogger(__name__)


class TestProfilePage(TestController):
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

#    def _setup_gpg_env(self):
#        self.homedir = tempfile.mkdtemp()
#        os.environ['GNUPGHOME'] = self.homedir
#
#    def _cleanup_gpg_env(self):
#        os.unsetenv('GNUPGHOME')
#        shutil.rmtree(self.homedir)
#
    def setUp(self):
        self._setup_example_user()
#        self._setup_gpg_env()
#        self._setup_models()
#        self._setup_example_countries()

    def tearDown(self):
        self._remove_example_user()
#        self._remove_example_countries()
#        self._cleanup_gpg_env()

    def test_index(self):
        # Test unauthenticated access to profile page
        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        self.assertIn(reverse('profile'), response.url)

        # Test login
        response = self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertIn('<a href="{}">'.format(reverse('logout')),
                      str(response.content))

        # Test /my redirect
        response = self.client.get(reverse('my'))
        self.assertEquals(response.status_code, 301)
        self.assertIn(reverse('profile'), response.url)

        # test user with country
        user = User.objects.get(email='email@example.com')
        country = Countries.objects.get(name='Germany')
        user.profile.country = country
        user.profile.save()

        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 200)
        self.assertIn('selected>Germany', str(response.content))

        # test DD user
#        user = meta.session.query(User) \
#            .filter(User.email == 'email@example.com') \
#            .one()
#        user.status = constants.USER_STATUS_DEVELOPER
#        meta.session.commit()
#      response = self.client.get(reverse(controller='profile', action='index'))
#        self.assertEquals(response.status_code, 200)
#        self.assertTrue('<a href="%s">' % (reverse('logout')) in response)
#
#        # test DM user
#        user = meta.session.query(User).filter(
#            User.email == 'email@example.com').one()
#        user.status = constants.USER_STATUS_MAINTAINER
#        meta.session.commit()
#      response = self.client.get(reverse(controller='profile', action='index'))
#        self.assertEquals(response.status_code, 200)
#        self.assertTrue('<a href="%s">' % (reverse('logout')) in response)
#
        # test handling of deleted user
        self._remove_example_user()
        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

#    def test__gpg(self):
#        response = self.client.post(reverse('profile'), {'form': 'gpg'})
#        self.assertEquals(response.status_code, 302)
#        self.assertTrue(response.location.endswith(reverse('login')))
#        response = self.client.post(reverse('login'), self._AUTHDATA)
#        user = meta.session.query(User) \
#            .filter(User.email == 'email@example.com') \
#            .one()
#        self.assertEquals(user.gpg, None)
#
#        # upload GPG key
#        response = self.client.post(reverse('profile'), {'form': 'gpg',
#                                             'delete_gpg': 0,
#                                             'commit': 'submit'},
#                                 upload_files=[('gpg', 'mykey.asc',
#                                               self._GPGKEY)])
#        self.assertEquals(response.status_code, 302)
#        self.assertTrue(response.location.endswith(reverse('profile')))
#        user = meta.session.query(User) \
#            .filter(User.email == 'email@example.com') \
#            .one()
#        self.assertEquals(user.gpg, self._GPGKEY)
#
#        # test whether index page contains GPG delete link
#      response = self.client.get(reverse(controller='profile', action='index'))
#        self.assertEquals(response.status_code, 200)
#        self.assertTrue('<a href="%s">' % (reverse('logout')) in response)
#        self.assertTrue(self._GPG_ID in response)
#
#        # delete GPG key
#        response = self.client.post(reverse('profile'), {'form': 'gpg',
#                                             'delete_gpg': 1,
#                                             'commit': 'submit',
#                                             'gpg': ''})
#        self.assertEquals(response.status_code, 302)
#        self.assertTrue(response.location.endswith(reverse('profile')))
#        user = meta.session.query(User) \
#            .filter(User.email == 'email@example.com') \
#            .one()
#        self.assertEquals(user.gpg, None)
#
#    def test__gpg_multi_keys(self):
#        response = self.client.post(reverse('profile'), {'form': 'gpg'})
#        self.assertEquals(response.status_code, 302)
#        self.assertTrue(response.location.endswith(reverse('login')))
#        response = self.client.post(reverse('login'), self._AUTHDATA)
#        user = meta.session.query(User) \
#            .filter(User.email == 'email@example.com') \
#            .one()
#        self.assertEquals(user.gpg, None)
#
#        # upload GPG key
#        response = self.client.post(reverse('profile'), {'form': 'gpg',
#                                             'delete_gpg': 0,
#                                             'commit': 'submit'},
#                                 upload_files=[('gpg', 'mykey.asc',
#                                               self._GPGKEY_MULTI)])
#        self.assertEquals(response.status_code, 200)
#        self.assertTrue('Multiple keys not supported' in response)
#        user = meta.session.query(User) \
#            .filter(User.email == 'email@example.com') \
#            .one()
#        self.assertEquals(user.gpg, None)
#
#    def test__gpg_wrong_email(self):
#        response = self.client.post(reverse('profile'), {'form': 'gpg'})
#        self.assertEquals(response.status_code, 302)
#        self.assertTrue(response.location.endswith(reverse('login')))
#        response = self.client.post(reverse('login'), self._AUTHDATA)
#        user = meta.session.query(User) \
#            .filter(User.email == 'email@example.com') \
#            .one()
#        self.assertEquals(user.gpg, None)
#
#        # upload GPG key
#        response = self.client.post(reverse('profile'), {'form': 'gpg',
#                                             'delete_gpg': 0,
#                                             'commit': 'submit'},
#                                 upload_files=[('gpg', 'mykey.asc',
#                                               self._GPGKEY_WRONG_EMAIL)])
#        self.assertEquals(response.status_code, 200)
#        self.assertTrue('None of your user IDs in key {} does match your'
#                       ' profile mail address'.format(self._GPG_ID_WRONG_EMAIL)
#                        in response)
#        user = meta.session.query(User) \
#            .filter(User.email == 'email@example.com') \
#            .one()
#        self.assertEquals(user.gpg, None)

    def test__details(self):
        response = self.client.post(reverse('profile'), {'form': 'details'})
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        response = self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.post(reverse('profile'), {
            'name': '',
            'email': 'email2@example.com',
            'commit_account': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertIn('This field is required.', str(response.content))
        response = self.client.post(reverse('profile'), {
            'name': 'Test user2',
            'email': 'email2@example.com',
            'commit_account': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))
        user = User.objects.filter(email='email@example.com')
        self.assertFalse(user)
        user = User.objects.get(email='email2@example.com')
        self.assertEquals(user.name, 'Test user2')
        user.delete()

    def test__password(self):
        response = self.client.post(reverse('profile'), {'form': 'password'})
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        # Login
        self.client.post(reverse('login'), self._AUTHDATA)

        # Test password change
        response = self.client.post(reverse('profile'), {
            'old_password': 'password',
            'new_password1': 'newpassword',
            'new_password2': 'newpassword',
            'commit_password': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))

        # Logout
        self.client.get(reverse('logout'))

        # Login with new password
        self.client.post(reverse('login'), {**self._AUTHDATA,
                                            'password': 'newpassword'})
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertIn('<a href="{}">'.format(reverse('logout')),
                      str(response.content))

    def test__other_details(self):
        response = self.client.post(reverse('profile'),
                                    {'form': 'other_details'})
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        response = self.client.post(reverse('login'), self._AUTHDATA)

        # test set ircnick
        response = self.client.post(reverse('profile'), {
            'form': 'other_details',
            'country': '',
            'ircnick': 'tester',
            'jabber': '',
            'status': UserStatus.contributor.value,
            'commit_profile': 'submit'
        })

        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))

        user = User.objects.get(email='email@example.com')
        self.assertEquals(user.profile.ircnick, 'tester')
        self.assertEquals(user.profile.status, UserStatus.contributor.value)

        # test DM switch
        response = self.client.post(reverse('profile'), {
            'form': 'other_details',
            'country': '',
            'ircnick': 'tester',
            'jabber': '',
            'status': UserStatus.maintainer.value,
            'commit_profile': 'submit'
        })

        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))

        user = User.objects.get(email='email@example.com')
        self.assertEquals(user.profile.status, UserStatus.maintainer.value)

        # A Maintainer cannot switch to DD
        response = self.client.post(reverse('profile'), {
            'form': 'other_details',
            'country': '',
            'ircnick': 'tester',
            'jabber': '',
            'status': UserStatus.developer.value,
            'commit_profile': 'submit'
        })

        self.assertEquals(response.status_code, 200)
        self.assertIn('errorlist', str(response.content))

        user = User.objects.get(email='email@example.com')
        self.assertEquals(user.profile.status, UserStatus.maintainer.value)

        # test DD view
        user.profile.status = UserStatus.developer.value
        user.profile.save()

        response = self.client.get(reverse('profile'))
        self.assertNotIn('Debian Maintainer (DM)', str(response.content))
        self.assertNotIn('Contributor', str(response.content))
        self.assertIn('Debian Developer (DD)', str(response.content))

        # A DD cannot switch to Maintainer
        response = self.client.post(reverse('profile'), {
            'form': 'other_details',
            'country': '',
            'ircnick': 'tester',
            'jabber': '',
            'status': UserStatus.contributor.value,
            'commit_profile': 'submit'
        })

        self.assertEquals(response.status_code, 200)
        self.assertIn('errorlist', str(response.content))

        user = User.objects.get(email='email@example.com')
        self.assertEquals(user.profile.status, UserStatus.developer.value)

        # Reset status
        user.profile.status = UserStatus.contributor.value
        user.profile.save()

#    def test__invalid_form(self):
#        response = self.client.post(reverse('profile'), {'form': 'invalid'})
#        self.assertEquals(response.status_code, 302)
#        self.assertTrue(response.location.endswith(reverse('login')))
#        response = self.client.post(reverse('login'), self._AUTHDATA)
#        response = self.client.post(reverse('profile'), {'form': 'invalid'})
#        self.assertEquals(response.status_code, 200)
#        self.assertTrue('<a href="%s">' % reverse('logout') in response)

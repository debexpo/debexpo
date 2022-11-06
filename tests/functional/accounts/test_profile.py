#   test_profile.py - Functional tests for the profile page
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2020 Baptiste Beauplat <lyknode@cilg.org>
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

from tests import TransactionTestController
from locale import getlocale, setlocale, LC_CTYPE
from django.urls import reverse
# from debexpo.lib import constants
# from debexpo.model import meta
from debexpo.accounts.models import Countries, User, UserStatus
from debexpo.keyring.models import Key
# from debexpo.model.user_countries import UserCountry
#
# import tempfile
# import os
# import shutil
#
# from passlib.hash import bcrypt
import logging

log = logging.getLogger(__name__)


class TestProfilePage(TransactionTestController):
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

    _GPGKEY_CORRUPTED = _GPGKEY_MULTI.replace('kMulGXK3', '')

    _GPGKEY_BAD_ALGO = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mQFCBF3L8/kRAwDIdoTIaE2JFjEehtnijhc9jJapRE/JSRbD/PGe5/cclRzNvg35
vkJrsaaZL2lEbPZij1HMqkDm+IaSJKwK2y/Ue2I1MjjPDCmOLGdnyXOfjCbEPBzL
A3OCc4yPC+qRdm8AoKkqkrZ7i0rrmcXlXI8vYzKpdQv7AwC7g2HdHNMxVs+8OKGt
GgZNqnAm2ob5SowWyHpmWRpmotuGkT9XTdj7oCuoYzweM0oH8EJlYuUYBRmvrueR
bOH3oOaj0jKNqw5gPbcmkNQXyj4qMhl08Q2AO3mgqEu2k2kC/iT5wXd9zeSssa/y
j2kNHr9jwnBfBxuQWVr5fPQqKB0iSV6j+rxcSw+C14YPwCbRoQoKCEUScNICyGWx
abL6bR3+gOfOfUaSFF8Qp1bl63yNIkxCA53GrVv6LnCBatD8yrQQQmFkIGFsZ28g
PGVAZS5lPoh4BBMRAgA4FiEECQEyfGXbNO2t+LV4ZvFIRqdbHm0FAl3L8/kCGwMF
CwkIBwIGFQoJCAsCBBYCAwECHgECF4AACgkQZvFIRqdbHm3WqACfWrV2orWa5DTn
s4mu8vYMiKeibHQAnA2YXiEFMRnYkleMh0vfJX+E0U6yuQENBF3L8/kQBADOCauB
Ut0OZJlujHhe3cunox3RG8XYoefBP85KiV6Pd95YW4F/4nyt8UFalyckblq54h0v
6sFEB+sp4yjn8P/8sIevJTRkrl6tS5qm/fVORzjRT5QZ4EkIV5rS8gusrI6Tm7Bb
tBOTocMZZxTR1hN/mASugB1WFtDLoTwBy5WmOwADBQP7BoN4zcUyQFwmCEtAITfs
XoyL86Nnvtx6SPUgLV6pPXLc9dBQfWEmzKJeenfezr1MmTEKMou2N7l+yiyhShAF
KLwSdfgrr9l6OpsDRW92NUq7FHtNegahOX1mFJFGRosQjTlchKfrc4BeZJ3mAXl3
lSBJDv0oJvaCY+2TlZpLSLqIYAQYEQIAIBYhBAkBMnxl2zTtrfi1eGbxSEanWx5t
BQJdy/P5AhsMAAoJEGbxSEanWx5tU3AAn01eDT24YshCLJD2oBh3E9C0kSbrAJ48
Bhc0DGRNF2chL7JwIIGcQSU8qA==
=IzuX
-----END PGP PUBLIC KEY BLOCK-----"""

    _GPGKEY_TOO_SMALL = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mI0EXcv0MAEEAM7cmSykJK0g3//gTe5KOazVqWYJ88jq6nGe/G54/1Ec1G+1DiyM
tS53YjcK7Ps9GD3ce1cDh43RPCRe2M9rOTEqBuCBvnPsSN+ix2S6v4yHVZZUmGgP
Aya+TGcnDSTFkp1FM4fDpe8OSV6lo4ivG+rIZuZNyj7Da4zuYL/a0pabABEBAAG0
EVRvbyBzbWFsbCA8ZkBmLmY+iM4EEwEKADgWIQSio63hNt7Cj/5EiqgKZL3S+hI1
lgUCXcv0MAIbAwULCQgHAgYVCgkICwIEFgIDAQIeAQIXgAAKCRAKZL3S+hI1lmM/
A/40BIw7IvbZX1gZWiuwpH0M7LWCPaKfEIndB0JIDXekC7yEMDY5vtqYaNU5glP4
7pSa2B2HorCe3z77AH5qrh2h06SudgvNFm2anyqM5lN94m43iGb+x5lL4DTL/0Uv
9xcFBo9Qv24TF2RClLQCj+pzM4XSFGzkbUWiyd8F1kEGNriNBF3L9DABBADHuz35
m5uzaimBHSzVWdIX9gjNn1fO6mIYZ/e/LwgNd0WjIIs8dHPTHZeFZG7qUJfP0I0t
SKm6rP7ymbIyR2dlf0dsrzYhc7LcFXh19XMBndNF42wPDDP80rB54CyvDUV2Gsl9
XyVP9K344FyRwlGt6/tGf7yBqhWxMLUFWE2bswARAQABiLYEGAEKACAWIQSio63h
Nt7Cj/5EiqgKZL3S+hI1lgUCXcv0MAIbDAAKCRAKZL3S+hI1lujXA/9lrVomxME/
DJP9w9cYD6YHpXfb7rsP1UUdGwHW/Yyo+AEyZRDBAE1ll9vbgDzToMBzKe/dSsTX
CcYlB0f1+5BWdumPRcFVZ56G1nXp8LhENIZJ42qCG73l5AnhgZnYoopOxWpjhApb
om5PZYZ7QbAdCs+jRBbIXLXyIKjdDEfyEw==
=Bjl+
-----END PGP PUBLIC KEY BLOCK-----"""

    _GPGKEY_CLEARTEXT = "Not a GPG key"

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

    _GPGKEY_2 = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEW/GBqhYJKwYBBAHaRw8BAQdA+6hBA4PcdcPwgMsKGQXrqwbJemLBgS1PkKZg
RFlKdKi0HVRlc3QgdXNlciA8ZW1haWxAZXhhbXBsZS5jb20+iJMEExYIADsCGwMF
CwkIBwIGFQoJCAsCBBYCAwECHgECF4AWIQRVkwbu4cjBst0cc7HENHgc6HHz3wUC
XyxWUwIZAQAKCRDENHgc6HHz30lxAP9Zvb7ssZ0bg94u2y1G3zbh8+5svSmGp3HT
hxMooIHvcwEA8jB3s5fVTZBIXagHBxACGSG5EhxlA8KlmaOSDGvl9w+0IHByaW1h
cnkgaWQgPHByaW1hcnlAZXhhbXBsZS5vcmc+iJAEExYIADgCGwMFCwkIBwIGFQoJ
CAsCBBYCAwECHgECF4AWIQRVkwbu4cjBst0cc7HENHgc6HHz3wUCXyxWUwAKCRDE
NHgc6HHz3zxDAQCB9zEqs0mWmriFqhXtRSwjhLhbprWxpAqkWTat6AU6XgD+MDVY
YgKEHeLuKqJ1MiR+x53f5ypxtA5eHJZdbs5OEA+0IlVURi04IMO8aWQgPHNlY29u
ZGFyeUBleGFtcGxlLm9yZz6IkAQTFggAOBYhBFWTBu7hyMGy3RxzscQ0eBzocfPf
BQJhaHZSAhsDBQsJCAcCBhUKCQgLAgQWAgMBAh4BAheAAAoJEMQ0eBzocfPfnboA
+wZMsDxIterEz3NJq/8DL9M+zGkw+m+a1i7vIoujsJOQAP9wQwRRDOE16vTjlj5B
cATF0DFQTkv7Efmh8pveItzzCbg4BFvxgaoSCisGAQQBl1UBBQEBB0A2uTeqr94/
VMRZ8VmqFHS9zPtgH1zn46e8xX7E7hbedAMBCAeIeAQYFggAIBYhBFWTBu7hyMGy
3RxzscQ0eBzocfPfBQJb8YGqAhsMAAoJEMQ0eBzocfPf8IcA/RyHF6zgRu2Ds3wH
8GgxjCZRW+YxWahX55/++pi9+bqyAQDp8rMxJeWXDntQn3RSfKfE7AnWF4Sd+aA+
S6LPuMUICrgzBF4JDZAWCSsGAQQB2kcPAQEHQD6/ZjyfzyP5bAhDeEKE9HvFrj2m
tFLIpGcYEP8BeEl9iO8EGBYKACAWIQRVkwbu4cjBst0cc7HENHgc6HHz3wUCXgkN
kAIbAgCBCRDENHgc6HHz33YgBBkWCgAdFiEEs897M/gHYzjbT6gOh5GSgxF1O9cF
Al4JDZAACgkQh5GSgxF1O9fQBwD+Ly2M/yKEzackdFfAGeuH+Ie/R5ISLewf6PR/
DL04EskA/2d7TWT0uQJemVLzKz7S7R7jnjkghuLDwPhOi6kPbmoKIggA/iHA2igz
psCWDYcNhNTEmXgsDSqUlLrqqde/3hDynhWeAP9jk7QAnDToELBdyCe6HpGXLC3q
6JoUgZicZ59g8ZdEAA==
=/JDz
-----END PGP PUBLIC KEY BLOCK-----"""

    OTHER_DETAIL_FORM = {
        'form': 'other_details',
        'country': '',
        'ircnick': '',
        'jabber': '',
        'language': '',
        'status': UserStatus.contributor.value,
        'commit_profile': 'submit'
    }

#    def _setup_gpg_env(self):
#        self.homedir = tempfile.mkdtemp()
#        os.environ['GNUPGHOME'] = self.homedir
#
#    def _cleanup_gpg_env(self):
#        os.unsetenv('GNUPGHOME')
#        shutil.rmtree(self.homedir)
#
    def setUp(self):
        self.locale = getlocale(LC_CTYPE)
        self._setup_example_user()
#        self._setup_gpg_env()
#        self._setup_models()
#        self._setup_example_countries()

    def tearDown(self):
        setlocale(LC_CTYPE, self.locale)
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

        # test DD view
        user.profile.status = UserStatus.developer.value
        user.profile.save()

        response = self.client.get(reverse('profile'))
        self.assertNotIn('Debian Maintainer (DM)', str(response.content))
        self.assertNotIn('Contributor', str(response.content))
        self.assertIn('Debian Developer (DD)', str(response.content))

        # test DM view
        user.profile.status = UserStatus.maintainer.value
        user.profile.save()

        response = self.client.get(reverse('profile'))
        self.assertIn('Debian Maintainer (DM)', str(response.content))
        self.assertIn('Contributor', str(response.content))
        self.assertNotIn('Debian Developer (DD)', str(response.content))

        # test handling of deleted user
        self._remove_example_user()
        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_gpg_encoding(self):
        setlocale(LC_CTYPE, 'C')

        self.client.post(reverse('login'), self._AUTHDATA)
        response = self.client.post(reverse('profile'), {
            'key': self._GPGKEY_2,
            'commit_gpg': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))

        user = User.objects.get(email='email@example.com')
        self.assertEquals(user.key.key, self._GPGKEY_2)

    def test__gpg(self):
        # Anonymous access to the form is denined
        response = self.client.post(reverse('profile'), {'form': 'gpg'})
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        # Authentication
        response = self.client.post(reverse('login'), self._AUTHDATA)

        # User has no key yet
        user = User.objects.get(email='email@example.com')
        self.assertRaises(Key.DoesNotExist, Key.objects.get, user=user)

        # Post GPG key
        response = self.client.post(reverse('profile'), {
            'key': self._GPGKEY,
            'commit_gpg': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))

        self.assertEquals(user.key.key, self._GPGKEY)

        # Again?
        response = self.client.post(reverse('profile'), {
            'key': self._GPGKEY,
            'commit_gpg': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))

        self.assertEquals(user.key.key, self._GPGKEY)

        # Update it
        response = self.client.post(reverse('profile'), {
            'key': self._GPGKEY_2,
            'commit_gpg': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))

        user = User.objects.get(email='email@example.com')
        self.assertEquals(user.key.key, self._GPGKEY_2)

        # Update it with bad key
        response = self.client.post(reverse('profile'), {
            'key': self._GPGKEY_BAD_ALGO,
            'commit_gpg': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertIn('errorlist', str(response.content))

        user = User.objects.get(email='email@example.com')
        self.assertEquals(user.key.key, self._GPGKEY_2)

        # test whether index page contains GPG delete link
        response = self.client.get(reverse('profile'))
        self.assertEquals(response.status_code, 200)
        self.assertIn('Fingerprint', str(response.content))
        self.assertIn('Remove', str(response.content))
        self.assertIn(self._GPGKEY_2.replace('\n', '\\n'),
                      str(response.content))

        # delete GPG key
        # The test is run twice here. First time for key deletion, second time
        # to ensure that debexpo does not crash on deleting a non-existing key.
        for loop in range(0, 2):
            response = self.client.post(reverse('profile'), {
                'key': self._GPGKEY,
                'delete_gpg': 'submit'
            })
            self.assertEquals(response.status_code, 200)
            self.assertNotIn('Fingerprint', str(response.content))
            self.assertNotIn('Remove', str(response.content))
            self.assertNotIn(self._GPGKEY.replace('\n', '\\n'),
                             str(response.content))
            self.assertRaises(Key.DoesNotExist, Key.objects.get, user=user)

    def _assert_gpg_post_failed(self, response, message):
        # User has no key yet
        user = User.objects.get(email='email@example.com')
        self.assertRaises(Key.DoesNotExist, Key.objects.get, user=user)

        # Assertions
        self.assertEquals(response.status_code, 200)
        self.assertIn('errorlist', str(response.content))
        self.assertIn(message, str(response.content))
        self.assertRaises(Key.DoesNotExist, Key.objects.get, user=user)

    def test__gpg_bad_keys(self):
        # Authentication
        response = self.client.post(reverse('login'), self._AUTHDATA)

        for key, message in (
            (self._GPGKEY_MULTI, 'Multiple keys not supported'),
            (self._GPGKEY_CORRUPTED, 'CRC error'),
            (self._GPGKEY_BAD_ALGO, 'Key algorithm not supported'),
            (self._GPGKEY_TOO_SMALL, 'Key size too small'),
            (self._GPGKEY_CLEARTEXT, 'no valid OpenPGP data'),
            ('', 'This field is required'),
        ):
            # Post GPG key
            response = self.client.post(reverse('profile'), {
                'key': key,
                'commit_gpg': 'submit'
            })

            self._assert_gpg_post_failed(response, message)

    def test_gpg_already_in_use(self):
        self._setup_example_user(True, 'another@example.org')

        response = self.client.post(reverse('login'), self._AUTHDATA)

        # Post GPG key
        response = self.client.post(reverse('profile'), {
            'key': self._GPGKEY,
            'commit_gpg': 'submit'
        })

        self._assert_gpg_post_failed(response, 'GPG Key already in use by '
                                               'another account')

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
            'email': 'email@example.com',
            'commit_account': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('errorlist', str(response.content))
        user = User.objects.get(email='email@example.com')
        self.assertEquals(user.name, 'Test user2')
        user.delete()

    def test__password(self):
        response = self.client.post(reverse('profile'), {'form': 'password'})
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        # Login
        self.client.post(reverse('login'), self._AUTHDATA)

        # Test password change, failed
        response = self.client.post(reverse('profile'), {
            'old_password': 'not-my-password',
            'new_password1': 'newpassword',
            'new_password2': 'newpassword',
            'commit_password': 'submit'
        })
        self.assertEquals(response.status_code, 200)
        self.assertIn('errorlist', str(response.content))

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

    def _set_profile(self, changes):
        user = User.objects.get(email='email@example.com')
        backup = {}

        for key, value in changes.items():
            backup[key] = getattr(user.profile, key)
            setattr(user.profile, key, value)

        user.profile.save()

        return backup

    def _test_other_details_with(self, changes, expected=None, init=None):
        if init:
            backup = self._set_profile(init)

        data = self.OTHER_DETAIL_FORM.copy()
        data.update(changes)

        response = self.client.post(reverse('profile'), data)

        self.assertEquals(response.status_code, 200)

        if expected:
            self.assertIn('errorlist', str(response.content))
        else:
            expected = data
            expected.pop('form')
            expected.pop('commit_profile')

            self.assertNotIn('errorlist', str(response.content))

        user = User.objects.get(email='email@example.com')

        for key, value in expected.items():
            if not value:
                self.assertFalse(getattr(user.profile, key))
            else:
                self.assertEquals(getattr(user.profile, key), value)

        if init:
            self._set_profile(backup)

        return response

    def test__other_details(self):
        response = self.client.post(reverse('profile'),
                                    {'form': 'other_details'})
        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        response = self.client.post(reverse('login'), self._AUTHDATA)

        self._test_other_details_with({'ircnick': 'tester'})
        self._test_other_details_with({'status': UserStatus.maintainer.value})
        self._test_other_details_with({'status': UserStatus.developer.value},
                                      {'status': UserStatus.maintainer.value})
        self._test_other_details_with(
            {'status': UserStatus.maintainer.value},
            {'status': UserStatus.developer.value},
            {'status': UserStatus.developer.value},
        )

#    def test__invalid_form(self):
#        response = self.client.post(reverse('profile'), {'form': 'invalid'})
#        self.assertEquals(response.status_code, 302)
#        self.assertTrue(response.location.endswith(reverse('login')))
#        response = self.client.post(reverse('login'), self._AUTHDATA)
#        response = self.client.post(reverse('profile'), {'form': 'invalid'})
#        self.assertEquals(response.status_code, 200)
#        self.assertTrue('<a href="%s">' % reverse('logout') in response)

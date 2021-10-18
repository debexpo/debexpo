#   test_hkp.py - Test HKP implementation
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2021 Baptiste Beauplat <lyknode@cilg.org>
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

from django.urls import reverse

from debexpo.keyring.models import SubKey

from tests import TestController

_GPGKEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

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


class TestHKP(TestController):
    def setUp(self):
        self._setup_example_user(gpg=True)
        another = self._setup_example_user(email='another@example.org')
        self._add_gpg_key(another, _GPGKEY,
                          'FINGERPRINT', '22', 256)

    def test_op(self):
        # Missing op parameter: 400
        response = self.client.get(reverse('hkp'))
        self.assertEquals(response.status_code, 400)
        self.assertIn("Missing 'op'", str(response.content))

        # Unknown op: 501
        response = self.client.get(reverse('hkp'),
                                   {'op': 'not-implemented'})
        self.assertEquals(response.status_code, 501)
        self.assertIn("Not Implemented", str(response.content))

    def test_get(self):
        # Missing search parameter: 400
        response = self.client.get(reverse('hkp'),
                                   {'op': 'get'})
        self.assertEquals(response.status_code, 400)
        self.assertIn("Missing 'search'", str(response.content))

        # No match: 404
        response = self.client.get(reverse('hkp'),
                                   {'op': 'get',
                                    'search': 'not-found'})
        self.assertEquals(response.status_code, 404)
        self.assertIn('Not Found', str(response.content))

        # Multiple matches: 500
        response = self.client.get(reverse('hkp'),
                                   {'op': 'get',
                                    'search': ''})
        self.assertEquals(response.status_code, 500)
        self.assertIn("Multiple matches found", str(response.content))

        # Matches long id: 200
        response = self.client.get(reverse('hkp'), {
            'op': 'get',
            'search': '0x' + self._GPG_FINGERPRINT[-16:]
        })
        self.assertEquals(response.status_code, 200)
        self.assertIn(self._GPG_KEY, response.content.decode())

        # Matches full fingerprint of a subkey: 200
        fingerprint = SubKey.objects.filter(
            key__fingerprint=self._GPG_FINGERPRINT).first().fingerprint
        response = self.client.get(reverse('hkp'), {
            'op': 'get',
            'search': fingerprint
        })
        self.assertIn(self._GPG_KEY, response.content.decode())
        self.assertEquals(response.status_code, 200)

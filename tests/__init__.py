#   __init__.py — Debexpo application test package
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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

"""
Debexpo application test package.

When the test runner finds and executes tests within this directory,
this file will be loaded to setup the test environment.
"""

from os import walk
from os.path import join
from logging import getLogger
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler, BaseHTTPRequestHandler
from threading import Thread

from django.test import TransactionTestCase, TestCase
# import tempfile
# from datetime import datetime
# from unittest import TestCase
#
from debexpo.accounts.models import User, Profile, UserStatus
from debexpo.keyring.models import GPGAlgo, Key
from debexpo.packages.models import Package, PackageUpload, SourcePackage, \
    Priority, Section, Distribution, Component, \
    BinaryPackage

__all__ = ['environ', 'url', 'TestController']

environ = {}

log = getLogger(__name__)


class DefaultTestController():
    """
    Base class for testing controllers.
    """

    _AUTHDATA = {'username': 'email@example.com',
                 'password': 'password',
                 'commit': 'submit'}

    _GPG_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

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
xOwJ1heEnfmgPkuiz7jFCAq4MwReCQ2QFgkrBgEEAdpHDwEBB0A+v2Y8n88j+WwI
Q3hChPR7xa49prRSyKRnGBD/AXhJfYjvBBgWCgAgFiEEVZMG7uHIwbLdHHOxxDR4
HOhx898FAl4JDZACGwIAgQkQxDR4HOhx8992IAQZFgoAHRYhBLPPezP4B2M420+o
DoeRkoMRdTvXBQJeCQ2QAAoJEIeRkoMRdTvX0AcA/i8tjP8ihM2nJHRXwBnrh/iH
v0eSEi3sH+j0fwy9OBLJAP9ne01k9LkCXplS8ys+0u0e4545IIbiw8D4ToupD25q
CiIIAP4hwNooM6bAlg2HDYTUxJl4LA0qlJS66qnXv94Q8p4VngD/Y5O0AJw06BCw
Xcgnuh6Rlywt6uiaFIGYnGefYPGXRAA=
=26Kz
-----END PGP PUBLIC KEY BLOCK-----"""

    _GPG_FINGERPRINT = '559306EEE1C8C1B2DD1C73B1C434781CE871F3DF'
    _GPG_TYPE = '22'
    _GPG_SIZE = 256
    _GPG_UIDS = [('primary id', 'primary@example.org'),
                 ('Test user', 'email@example.com')]

    def _add_gpg_key(self, user, data, fingerprint, algo, size):
        key = Key()
        key.key = data
        key.fingerprint = fingerprint
        key.user = user
        key.algorithm = GPGAlgo.objects.get(gpg_algorithm_id=algo)
        key.size = size
        key.save()
        key.update_subkeys()

    def _setup_example_user(self, gpg=False, email='email@example.com'):
        """Add an example user.

        The example user with name ``Test user``, email address
        ``email@example.com`` and password ``password`` is added to
        the database.

        This method may be used in the setUp method of derived test
        classes.
        """
        # Create a test user and save it.
        user = User.objects.create_user(email, 'Test user', 'password')
        user.save()
        profile = Profile(user=user, status=UserStatus.contributor.value)
        profile.save()

        if gpg:
            self._add_gpg_key(user, self._GPG_KEY, self._GPG_FINGERPRINT,
                              self._GPG_TYPE, self._GPG_SIZE)

    def _remove_example_user(self):
        """Remove the example user.

        This method removes the example user created in
        _setup_example_user.

        This method must be used in the tearDown method of derived
        test classes that use _setup_example_user.
        """
        user = User.objects.filter(email='email@example.com')
        user.delete()

    def _setup_example_package(self):
        """Add an example package.

        The example package with name ``testpackage`` is added to
        the database.

        This method may be used in the setUp method of derived test
        classes.
        """
        user = User.objects.get(email='email@example.com')

        package = Package.objects.get_or_create(name='testpackage')[0]

        package_upload = PackageUpload(
            uploader=user,
            package=package,
            version='1.0-1',
            distribution=Distribution.objects.get_or_create(name='unstable')[0],
            component=Component.objects.get_or_create(name='main')[0],
            closes='943216')
        package_upload.save()

        source = SourcePackage(
            upload=package_upload,
            maintainer='Test User <email@example.com>',
            section=Section.objects.get_or_create(name='admin')[0],
            priority=Priority.objects.get_or_create(name='optional')[0]
        )

        source.save()

        binary = BinaryPackage(
            upload=package_upload,
            name='testpackage',
            description='A short description here',
        )

        binary.save()

        package = Package.objects.get_or_create(name='anotherpackage',
                                                in_debian=True)[0]

        package_upload = PackageUpload(
            uploader=user,
            package=package,
            version='1.0-1',
            distribution=Distribution.objects.get_or_create(name='buster')[0],
            component=Component.objects.get_or_create(name='non-free')[0],
            closes='')
        package_upload.save()

        source = SourcePackage(
            upload=package_upload,
            maintainer='Another maintainer <another@example.com>',
            section=Section.objects.get_or_create(name='utils')[0],
            priority=Priority.objects.get_or_create(name='standard')[0]
        )
        source.save()

        binary = BinaryPackage(
            upload=package_upload,
            name='libanotherpackage',
            description='Another short description here',
        )

        binary.save()

    def _remove_example_package(self):
        """Remove the example package.

        This method removes the example package created in
        _setup_example_package.

        This method must be used in the tearDown method of derived
        test classes that use _setup_example_package.
        """

        for name in ('testpackage', 'anotherpackage'):
            try:
                package = Package.objects.get(name=name)
            except Package.DoesNotExist:
                pass
            else:
                package.delete()

    def _assert_no_leftover(self, path):
        matches = self._find_all('', path)

        for match in matches:
            log.error('leftover: {}'.format(match))

        self.assertFalse(matches)

    def _find_all(self, name, path):
        """Find a file in a path"""
        result = []
        for root, dirs, files in walk(path):
            for filename in files:
                if name in filename:
                    result.append(join(root, filename))
        return result


class InfinityHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.end_headers()
        while True:
            try:
                self.wfile.write(bytes(''.zfill(4 * 1024 * 1024), 'UTF-8'))
            except Exception:
                break


class TestingTCPServer(TCPServer):
    allow_reuse_address = True


class TestingHTTPServer():
    def __init__(self, handler=None, port=0):
        if not handler:
            handler = SimpleHTTPRequestHandler

        self.httpd = TestingTCPServer(("localhost", port), handler)
        _, self.port = self.httpd.server_address
        self.thread = Thread(target=self.httpd.serve_forever)

    def __enter__(self):
        self.thread.start()

        return self

    def __exit__(self, type, value, traceback):
        self.httpd.shutdown()


class TransactionTestController(DefaultTestController,
                                TransactionTestCase):
    serialized_rollback = True


class TestController(DefaultTestController, TestCase):
    pass

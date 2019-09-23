# -*- coding: utf-8 -*-
#
#   __init__.py — Pylons application test package
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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
Pylons application test package.

When the test runner finds and executes tests within this directory,
this file will be loaded to setup the test environment.

It registers the root directory of the project in sys.path and
pkg_resources, in case the project hasn't been installed with
setuptools. It also initializes the application via websetup (paster
setup-app) with the project's test.ini configuration file.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import md5
import tempfile
from datetime import datetime
from unittest import TestCase

from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test
from debexpo.model import meta, import_all_models
from debexpo.model.users import User
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion
from debexpo.model.source_packages import SourcePackage
from debexpo.model.user_upload_key import UserUploadKey
from debexpo.model.user_countries import UserCountry
from debexpo.lib.gnupg import GnuPG

__all__ = ['environ', 'url', 'TestController']

SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}


class TestController(TestCase):
    """
    Base class for testing controllers.
    """

    _AUTHDATA = {'email': 'email@example.com',
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
xOwJ1heEnfmgPkuiz7jFCAo=
=xgUN
-----END PGP PUBLIC KEY BLOCK-----"""

    _GPG_ID = '256E/E871F3DF'

    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

    def _setup_models(self):
        """Create all models in the test database."""
        # Since we are using a sqlite database in memory (at least that's what
        # the default in test.ini is), we need to create all the tables
        # necessary. So let's import all the models and create all the tables.
        import_all_models()
        meta.metadata.create_all(bind=meta.engine)

    def _setup_example_countries(self):
        """Add a few example countries.

        Adds ``United States``, ``Germany``, ``Russia`` and ``United Kingdom``.
        """
        for name in ('United States', 'Germany', 'Russia', 'United Kingdom'):
            meta.session.add(UserCountry(name=name))
        meta.session.commit()

    def _remove_example_countries(self):
        """Remove the example countries."""
        meta.session.query(UserCountry).delete()
        meta.session.commit()

    def _add_gpg_key(self, key, key_id=None, user=None):
        gpg_ctl = GnuPG()

        # Add key to keyring
        temp = tempfile.NamedTemporaryFile(delete=True)
        temp.write(key)
        temp.flush()
        gpg_ctl.add_signature(temp.name)
        temp.close()

        # Update user in database
        if user:
            user.gpg = key
            user.gpg_id = key_id
            meta.session.merge(user)
            meta.session.commit()

    def _setup_example_user(self, gpg=False):
        """Add an example user.

        The example user with name ``Test user``, email address
        ``email@example.com`` and password ``password`` is added to
        the database.

        This method may be used in the setUp method of derived test
        classes.
        """
        # Create a test user and save it.
        user = User(name='Test user', email='email@example.com',
                    password=md5.new('password').hexdigest(),
                    lastlogin=datetime.now())

        meta.session.add(user)
        meta.session.commit()

        if meta.session.query(UserUploadKey).filter_by(
                upload_key='upload_key').count() == 0:
            user_upload_key = UserUploadKey(
                user_id=user.id,
                upload_key='upload_key')
            meta.session.add(user_upload_key)
            meta.session.commit()

        if gpg:
            self._add_gpg_key(self._GPG_KEY, self._GPG_ID, user)

    def _remove_example_user(self):
        """Remove the example user.

        This method removes the example user created in
        _setup_example_user.

        This method must be used in the tearDown method of derived
        test classes that use _setup_example_user.
        """
        meta.session.query(User) \
            .filter(User.email == 'email@example.com') \
            .delete()
        meta.session.commit()

    def _setup_example_package(self):
        """Add an example package.

        The example package with name ``testpackage`` is added to
        the database.

        This method may be used in the setUp method of derived test
        classes.
        """
        user = meta.session.query(User).filter(
            User.email == 'email@example.com').one()

        if not user:
            raise Exception('Example user must be created before the package')

        package = Package(name='testpackage', user=user,
                          description='a test package')
        meta.session.add(package)

        package_version = PackageVersion(
            package=package,
            version='1.0-1',
            maintainer='Test User <email@example.com>',
            section='Admin',
            distribution='unstable',
            qa_status=0,
            component='main',
            priority='optional',
            closes='',
            uploaded=datetime.now())
        meta.session.add(package_version)
        meta.session.add(SourcePackage(package_version=package_version))
        meta.session.commit()

    def _remove_example_package(self):
        """Remove the example package.

        This method removes the example package created in
        _setup_example_package.

        This method must be used in the tearDown method of derived
        test classes that use _setup_example_package.
        """
        package = meta.session.query(Package) \
            .filter(Package.name == 'testpackage') \
            .first()
        if not package:
            return

        package_version = meta.session.query(PackageVersion) \
            .filter(PackageVersion.package == package) \
            .first()

        package_source = meta.session.query(SourcePackage) \
            .filter(SourcePackage.package_version == package_version) \
            .first()

        meta.session.delete(package_source)
        meta.session.delete(package_version)
        meta.session.delete(package)
        meta.session.commit()

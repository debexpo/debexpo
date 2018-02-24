# -*- coding: utf-8 -*-
#
#   __init__.py — Pylons application test package
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
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

import os
import sys
import md5
from datetime import datetime
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test
from debexpo.model import meta, import_all_models
from debexpo.model.users import User
from debexpo.model.user_upload_key import UserUploadKey
from debexpo.model.user_countries import UserCountry

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

    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

    def _setup_models(self):
        """Create all models in the test database."""
        # Since we are using a sqlite database in memory (at least that's what the default in
        # test.ini is), we need to create all the tables necessary. So let's import all the models
        # and create all the tables.
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

    def _setup_example_user(self):
        """Add an example user.

        The example user with name ``Test user``, email address
        ``email@example.com`` and password ``password`` is added to
        the database.

        This method may be used in the setUp method of derived test
        classes.
        """
        # Create a test user and save it.
        user = User(name='Test user', email='email@example.com',
                    password=md5.new('password').hexdigest(), lastlogin=datetime.now())

        meta.session.add(user)
        meta.session.commit()

        if meta.session.query(UserUploadKey).filter_by(
                upload_key='upload_key').count() == 0:
            user_upload_key = UserUploadKey(
                user_id=user.id,
                upload_key='upload_key')
            meta.session.add(user_upload_key)
            meta.session.commit()


    def _remove_example_user(self):
        """Remove the example user.

        This method removes the example user created in
        _setup_example_user.

        This method must be used in the tearDown method of derived
        test classes that use _setup_example_user.
        """
        meta.session.query(User).filter(User.email=='email@example.com').delete()
        meta.session.commit()

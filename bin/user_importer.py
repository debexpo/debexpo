# -*- coding: utf-8 -*-
#
#   debexpo-importer — executable script to import new packages
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2011 Asheesh Laroia <paulproteus@debian.org>
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

""" Executable script to import new packages. """

__author__ = 'Asheesh Laroia'
__copyright__ = 'Copyright © 2011 Asheesh Laroia'
__license__ = 'MIT'

import simplejson

from optparse import OptionParser
import datetime
import logging
import sys
import os

from debexpo.model import meta
import debexpo.model.users
from paste.deploy import appconfig
from debexpo.config.environment import load_environment

import pylons

def import_users(list_of_dicts):
    for d in list_of_dicts:
        import_one_user(d)

def import_one_user(data_dict):
    '''This imports user data. It expects the following keys:
    * realname
    * email
    * gpgkey
    * password

    It checks if that email address already exists; if so, it logs
    a warning indicating that are skipping the user.

    If the user ought to be imported, then we do it! If we succeed, we print
    nothing. If we fail, we abort.'''
    transformation = {
        'realname': 'name',
        'gpgkey': 'gpg',
        'email': 'email',
        'password': 'password'
        }

    # First, make sure that the data_dict has everything we need
    for key in transformation:
        if key not in data_dict:
            raise ValueError, ("Missing a key from data_dict: %s" % key)

    # Then, see if the email address matches a current user
    user_email = data_dict['email']
    matches = meta.session.query(debexpo.model.users.User
            ).filter_by(email=user_email)
    if matches.count():
        logging.warn("A user with email address %s already exists" % (
                user_email,))
        return

    # Okay! Let's convert the data format...
    transformed = {}
    for oldkey in transformation:
        newkey = transformation[oldkey]
        transformed[newkey] = data_dict[oldkey]

    # Add an email address verification key, though it is not truly necessary
    transformed['lastlogin'] = datetime.datetime(1970, 1, 1, 0, 0, 0)

    # ...and then we truly create the account!
    u = debexpo.model.users.User(**transformed)
    meta.session.add(u)
    meta.session.commit()

def main():
    parser = OptionParser(usage="%prog -u FILE -i FILE")
    parser.add_option('-u', '--user-json-path', dest='user_json_path',
                      help='Path to JSON file with user data to import (/dev/stdin is permissible)',
                      metavar='FILE', default=None)
    parser.add_option('-i', '--ini', dest='ini',
                      help='Path to application ini file',
                      metavar='FILE', default=None)

    (options, args) = parser.parse_args()

    if not options.user_json_path:
        parser.print_help()
        sys.exit(1)

    # Initialize Pylons app
    conf = appconfig('config:' + os.path.abspath(options.ini))
    pylons.config = load_environment(conf.global_conf, conf.local_conf)


    list_of_dicts = simplejson.load(open(options.user_json_path))

    import_users(list_of_dicts)
    return 0

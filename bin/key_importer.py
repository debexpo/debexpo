#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#   key_importer.py — Regenerate the mentors keyring from scratch
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2012 Arno Töll <debian@toell.net>
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
Update the mentors keyring cyclically
"""

from __future__ import print_function

__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2012 Arno Töll'
__license__ = 'MIT'

import datetime
import tempfile
import shutil
import os.path
import sys
import optparse
import pylons


from paste.deploy import appconfig
from debexpo.config.environment import load_environment
from debexpo.model.users import User
from debexpo.model import meta
from debexpo.lib.gnupg import GnuPG


class UpdateKeyring(object):
    def __init__(self, inifile):
        """
        This method does nothing in this cronjob
        """
        self.inifile = os.path.abspath(inifile)
        conf = appconfig('config:' + self.inifile)
        pylons.config = load_environment(conf.global_conf, conf.local_conf)
        self.config = pylons.config
        self.gpg = GnuPG()

    def invoke(self):
        """
        Loops through the debexpo.upload.incoming directory and runs the debexpo.importer for each file
        """

        if 'debexpo.gpg_keyring' not in self.config:
            print("debexpo.gpg_keyring was not configured or is not writable")
            return

        try:
            keyring = open(self.config['debexpo.gpg_keyring'], "a+")
            keyring.close()
        except IOError as e:
            print("Can't access file: %s: %s" % (self.config['debexpo.gpg_keyring'], str(e)))
            return

        print("Regenerate keyring into %s" % (keyring.name))
        (_, keyring) = tempfile.mkstemp()
        for user in meta.session.query(User).all():
            if not user.gpg:
                continue
            temp = tempfile.NamedTemporaryFile(delete=True)
            temp.write(user.gpg)
            temp.flush()
            (out, err) = self.gpg.add_signature(temp.name, keyring)
            temp.close()
            if err != 0:
                print("gpg failed to import keyring: %s" % (out))
                continue
            print(out)

        shutil.move(keyring, self.config['debexpo.gpg_keyring'])

        meta.session.close()


if __name__=='__main__':
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ini", dest="ini", help="path to application ini file", metavar="FILE")
    (options, args) = parser.parse_args()
    if not options.ini:
        parser.print_help()
        sys.exit(0)
    run = UpdateKeyring(options.ini)
    run.invoke()

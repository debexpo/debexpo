# -*- coding: utf-8 -*-
#
#   updatekeyring.py — Update the mentors keyring cyclically
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2012 Arno Töll'
__license__ = 'MIT'

from debexpo.model.data_store import DataStore
from debexpo.model.users import User
from debexpo.model import meta

from debexpo.cronjobs import BaseCronjob
from debexpo.lib.gnupg import GnuPG


import datetime
import tempfile
import shutil

class UpdateKeyring(BaseCronjob):
    def setup(self):
        """
        This method does nothing in this cronjob
        """
        self._last_trigger = 0
        self.log.debug("%s loaded successfully" % (__name__))
        self.gpg = GnuPG()

    def teardown(self):
        """
        This method does nothing in this cronjob
        """
        pass

    def invoke(self):
        """
        Loops through the debexpo.upload.incoming directory and runs the debexpo.importer for each file
        """

        if 'debexpo.gpg_keyring' not in self.config:
            self.log.critical("debexpo.gpg_keyring was not configured or is not writable")
            return

        try:
            keyring = open(self.config['debexpo.gpg_keyring'], "a+")
            keyring.close()
        except IOError as e:
            self.log.critical("Can't access file: %s: %s" % (self.config['debexpo.gpg_keyring'], str(e)))
            return

        gpg_generator = meta.session.query(DataStore).filter(DataStore.namespace == "_gpg_").filter(DataStore.code == "generator_datetime").first()

        gpg_generator.value = float(gpg_generator.value)
        if not gpg_generator:
            return

        if gpg_generator.value > self._last_trigger:
            self.log.info("Regenerate keyring into %s" % (keyring.name))
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
                    self.log.critical("gpg failed to import keyring: %s" % (out))
                    continue
                self.log.debug(out)

            shutil.move(keyring, self.config['debexpo.gpg_keyring'])
            self._last_trigger = gpg_generator.value

        meta.session.close()


cronjob = UpdateKeyring
schedule = datetime.timedelta(hours = 6)

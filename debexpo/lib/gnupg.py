# -*- coding: utf-8 -*-
#
#   utils.py — Debexpo utility functions
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Serafeim Zanikolas <serzan@hellug.gr>
#               2011 Arno Töll <debian@toell.net>
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
Wrapper for a subset of GnuPG functionality.
"""

__author__ = 'Serafeim Zanikolas, Arno Töll'
__copyright__ = 'Copyright © 2008 Serafeim Zanikolas, 2011 Arno Töll'
__license__ = 'MIT'

import logging
import os
import subprocess

from pylons import config

log = logging.getLogger(__name__)

class GnuPG(object):

    GPG_PATH_NOT_INITIALISED = -1
    INVALID_GNUPG_RUN_INVOCATION = -2

    def __init__(self):
        """
        Wrapper for certain GPG operations.

        Meant to be instantiated only once.
        """
        self.gpg_path = config.get('debexpo.gpg_path')
        if self.gpg_path is None:
            log.error('debexpo.gpg_path is not set in configuration file' +
                      ' (or is set to a blank value)')
        elif not os.path.isfile(self.gpg_path):
            log.error('debexpo.gpg_path refers to a non-existent file')
            self.gpg_path = None
        elif not os.access(self.gpg_path, os.X_OK):
            log.error('debexpo.gpg_path refers to a non-executable file')
            self.gpg_path = None

    def is_unusable(self):
        """Returns true if the gpg binary is not installed or not executable."""
        return self.gpg_path is None

    def parse_key_id(self, key):
        """
        Returns the key id of the given GPG public key.

        ``key``
            ASCII armored GPG public key.

        Sample output to be parsed:

        pub  1024D/355304E4 2005-09-13 Serafeim Zanikolas <serzan@hellug.gr>
        sub  1024g/C082E9B7 2005-09-13 [expires: 2008-09-12]

        """
        try:
            (output, _) = self._run(stdin=key)
            lines = output.split('\n')
            for line in lines:
                if line.startswith('pub'):
                    # get only the 2nd column of the 1st matching line
                    return line.split()[1]
        except (AttributeError, IndexError):
            log.error("Failed to extract key id from gpg output: '%s'"
                       % output)

    def verify_sig(self, signed_file, pubring=None):
        """
        Returns true if the given GPG-signed file can be verified.

        ``signed_file``
             path to signed file
        ``pubring``
             path to public key ring (when not specified, the default GPG
             setting will be used (~/.gnupg/pubring.gpg))
        """
        if pubring is None:
            args = ('--verify', )
        else:
            args = ('--verify', '--keyring', pubring, '--no-default-keyring', signed_file)
        (_, status) = self._run(args=args)
        return status == 0

    def _run(self, stdin=None, args=None):
        """
        Run gpg with the given stdin and arguments and return the output and
        exit status.

        ``stdin``
            Feed gpg with this input to stdin
        ``args``
            a list of strings to be passed as argument(s) to gpg

        """
        if self.gpg_path is None:
            return (None, GnuPG.GPG_PATH_NOT_INITIALISED)

        cmd = [ self.gpg_path, ]
        if not args is None:
                cmd.extend(args)

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (output, _) = process.communicate(input=stdin)
        status = process.returncode

        if status != 0:
            return (None, status)
        return (output, 0)


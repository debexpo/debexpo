# -*- coding: utf-8 -*-
#
#   utils.py — Debexpo utility functions
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Serafeim Zanikolas <serzan@hellug.gr>
#             © 2011 Arno Töll <debian@toell.net>
#             © 2012 Clément Schreiner <clement@mux.me>
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

__author__ = 'Serafeim Zanikolas, Arno Töll, Clément Schreiner'
__copyright__ = ','.join(['Copyright © 2008 Serafeim Zanikolas',
                         '2011 Arno Töll',
                         '2012 Clément Schreiner',
                         ])
__license__ = 'MIT'

import logging
import os
import subprocess
import re

log = logging.getLogger(__name__)

GPG_SIGNATURE_PATTERN = r"^.*Signature made.*using (?P<key_type>\S+) key ID (?P<key_id>\w+)$"
GPG_ADDR_PATTERN = r"^(pub\s+(?P<key_id>\S+)\s+(?P<key_date>\S+)\s|uid\s+)(?P<uid_name>.+)\s+<(?P<uid_email>.+?)>$"

class GpgFile(object):
    GPG_ARGS = ['--decrypt']

    def __init__(self, gpg, data=None, filename=None):
        """ Loads a file and verifies its PGP signature """
        self.gpg = gpg

        self.key_id = None
        self.key_type = None
        self.data = None

        self.is_signed = False
        self.valid = False
        self.loaded = False

        if data is not None:
            self._load_data(data)
        elif filename is not None:
            self._load_file(filename)

    def _load_data(self, data):
        (out, err, code) = self.gpg.run(args=GpgFile.GPG_ARGS,
                                         stdin=data,
                                         pubring=None)
        self._parse_gpg_result(out, err, code)
        self.loaded = True

    def _load_file(self, filename):
        args = GpgFile.GPG_ARGS
        args.append(filename)
        (out, err, code) = self.gpg.run(args=args,
                                        pubring=None)
        self._parse_gpg_result(out, err, code)
        self.loaded = True

    def _parse_gpg_result(self, out, err, code):
        if code != 0:
            return

        line_err = err.split('\n')[0]
        m = re.search(GPG_SIGNATURE_PATTERN, line_err)
        if m is not None:
            self.is_signed = True
            self.key_id = m.group('key_id')
            self.key_type = m.group('key_type')
            self.valid = True
            self.data = out

class GpgKey(object):
    def __init__(self, gpg, data=None):
        """ Loads a PGP public key block """

        self.gpg = gpg

        self.key_strength = None
        self.key_type = None
        self.key_id = None

        self.key_date = None
        self.user_ids = []
        self.loaded = False
        self.valid = False

        if data is not None:
            self._load_data(data)

    def _load_data(self, data):
        (out, err, code) = self.gpg.run(stdin=data)
        self._parse_gpg_result(out, err, code)
        self.loaded = True

    def _parse_gpg_result(self, out, err, code):
        if code != 0:
            return
        out = unicode(out, encoding='utf-8', errors='replace')
        lines = (out.split('\n'))
        for line in lines:
            m = re.match(GPG_ADDR_PATTERN, line)
            if m is not None:
                if (self.key_id is None
                    and m.group('key_id') is not None):
                    self.parse_key_string(m.group('key_id'))
                self.user_ids.append((m.group('uid_name'),
                                      m.group('uid_email')))

        self.valid = True

    def parse_key_string(self, s):
        """
        for example '4096R/8123F27C'
        4096 -> key strength
        R -> key type
        8123F27C -> key id
        """
        (tmp, self.key_id) = s.split('/', 1)
        self.key_strength = int(tmp [:-1])
        self.key_type = tmp[-1]

class GnuPG(object):
    GPG_PATH_NOT_INITIALISED = -1
    INVALID_GNUPG_RUN_INVOCATION = -2

    def __init__(self, gpg_path, default_keyring):
        self.gpg_path = gpg_path
        self.default_keyring = default_keyring

        if self.gpg_path is None:
            print "No gpg"

        elif not os.path.isfile(self.gpg_path):
            self.gpg_path = None

        elif not os.access(self.gpg_path, os.X_OK):
            self.gpg_path = None

        if self.default_keyring is None:
            print "No keyring"

    def add_signature(self, filename, pubring=None):
        args = ('--import-options', 'import-minimal', '--import', signature_file)
        return self.run(args=args, pubring=pubring)

    def remove_signature(self, keyid, pubring=None):
        args = ('--yes', '--delete-key', keyid)
        return self.run(args=args, pubring=pubring)

    def is_unusable(self):
        """Returns true if the gpg binary is not installed or not executable."""
        return self.gpg_path is None

    def run(self, stdin=None, args=None, pubring=None):
        """
        Run gpg with the given stdin and arguments and return the output
        (stdout and stderr) and exit status.

        ``stdin``
            Feed gpg with this input to stdin
        ``args``
            a list of strings to be passed as argument(s) to gpg
        ``pubring``
            the path to the public gpg keyring. Note that
            ``pubring + ".secret"`` will be used as the private keyring

        """
        if self.gpg_path is None:
            return (None, None, GnuPG.GPG_PATH_NOT_INITIALISED)

        if pubring is None:
            pubring = self.default_keyring

        cmd = [
            self.gpg_path,
            '--no-options',
            '--batch',
            '--no-default-keyring',
            '--secret-keyring', pubring + ".secret",
            '--keyring', pubring,
            ]
        if not args is None:
            cmd.extend(args)

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (output, outerr) = process.communicate(input=stdin)
        status = process.returncode

        return (output, outerr, status)

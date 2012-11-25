# -*- coding: utf-8 -*-
#
#   gnupg.py — GnuPG wrapper
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
from collections import namedtuple

log = logging.getLogger(__name__)


#
# Regular expressions for parsing gnupg's output
#

GPG_ADDR_PATTERN = r"^(pub\s+(?P<key_id>\S+)\s+(?P<key_date>\S+)\s|uid\s+)(?P<uid_name>.+)\s+<(?P<uid_email>.+?)>$"


#
# Result objects
#

GpgFileSignature = namedtuple('GpgFileSignature',
                              ['is_valid',  # boolean: signature status
                               'key_id',
                               'data',  # plaintext
                               ])

GpgKey = namedtuple('GpgKey', ['id', 'type', 'strength'])

GpgKeyBlock = namedtuple('GpgKeyBlock', ['key', 'user_ids'])

GpgUserId = namedtuple('GpgUserId', ['user', 'email'])

# generic object for other results
GpgResult = namedtuple('GpgResult', ['code', 'out', 'err',
                                     'status', 'success'])


#
# Exceptions
#

class GpgPathNotInitialised(Exception):
    """ GnuPG has not been initialised properly """

class MissingPublicKeyring(Exception):
    """ No public keyring has been provided """

class InvalidGnupgRunInvocation(Exception):
    """ GnuPG has not been run properly  """

class GpgVerifyNoData(Exception):
    """ No data has been given to gnupg --decrypt """

class GpgVerifyInvalidData(Exception):
    """ Invalid data given to gnupg --decrypt """

class GpgFailure(Exception):
    """ Generic exception for errors while running gnupg """

class GpgMissingData(Exception):
    """ Some data is missing for the gpg command. """


#
# Main class
#

class GnuPG(object):
    """ Wrapper for some GnuPG operations """

    def __init__(self, gpg_path='/usr/bin/gpg',
                 default_keyring='~/.gnupg/keyring.gpg'):
        self.gpg_path = gpg_path
        self.default_keyring = os.path.expanduser(default_keyring)

        if self.gpg_path and not os.path.isfile(self.gpg_path):
            self.gpg_path = None

        elif self.gpg_path and not os.access(self.gpg_path, os.X_OK):
            self.gpg_path = None

        if self.gpg_path is None or self.default_keyring is None:
            self.unusable = True

    @staticmethod
    def string2key(s):
        """
        for example '4096R/8123F27C'
        4096 -> key strength
        R -> key type
        8123F27C -> key id
        Returns a GpgKey object.
        """

        (tmp, key_id) = s.split('/', 1)
        key_strength = int(tmp [:-1])
        key_type = tmp[-1]
        key = GpgKey(key_id, key_type, key_strength)
        return key

    @staticmethod
    def key2string(k):
        """
        Reverse function for string2key"
        """
        s = "{0}{1}/{2}".format(k.strength,
                             k.type,
                             k.id)
        return s

    @property
    def is_unusable(self):
        """Returns true if the gpg binary is not installed or not executable."""
        return self.gpg_path is None

    def verify_file(self, path=None, file_object=None, data=None, pubring=None):
        """
        Check the status of the given's file signature.
        If ``path`` is not None, pass it as an argument to gnupg.
        Else, if ``file_object`` is not None, pass its content to
        gnupg's stdin.
        """

        # cmd: --decrypt
        args = ['--decrypt']

        keywords_args = {'pubring': pubring}
        if path is not None and os.path.isfile(path):
            args.append(path)
        elif file_object is not None:
            if file_object.is_closed:
                raise GpgVerifyInvalidData
            else:
                data = file_object.read()
                keywords_args['stdin'] = data
        elif data is not None:
            keywords_args['stdin'] = data
        else:
            raise GpgVerifyNoData

        (out, err, status, code) = self._run(args=args,
                                     **keywords_args)
        return self._parse_verify_result(out, err, status, code)

    def _parse_verify_result(self, out, err, status, code):
        # documentation for status lines in /usr/share/doc/gnupg/DETAILS
        key_id = None
        is_valid = False
        data = None

        for line in status:
            if line[0] == 'ERRSIG' and line[6] == '9':
                raise GpgFailure('Unknown key')
            if line[0] == 'BADSIG':
                is_valid = False
            elif line[0] == 'GOODSIG':
                is_valid = True
                key_id = line[1]
                data = out
        return GpgFileSignature(is_valid=is_valid,
                                key_id=key_id,
                                data=data)

    def parse_key_block(self, data=None, path=None):
        """
        Parse a PGP public key block
        """


        stdin = None
        args = []

        if data is not None:
            stdin = data
        elif path is not None:
            args.append(path)

        else:
            raise GpgMissingData

        (out, err, status, code) = self._run(stdin, args)
        return self._parse_key_block_result(out, err, code)

    def _parse_key_block_result(self, out, err, code):
        if code != 0:
            return GpgKeyBlock(None, None)

        # FIXME: use the system's encoding instead of utf-8
        out = unicode(out, encoding='utf-8', errors='replace')
        lines = (out.split('\n'))

        key = None
        user_ids = []
        for line in lines:
            m = re.match(GPG_ADDR_PATTERN, line)
            if m is not None:
                if (key is None
                    and m.group('key_id') is not None):
                    key = self.string2key(m.group('key_id'))

                if (m.group('uid_name') is not None
                    and m.group('uid_email') is not None):
                    uid_name = m.group('uid_name')
                    uid_email = m.group('uid_email')
                    user_id = GpgUserId(uid_name, uid_email)
                    user_ids.append(user_id)

        if key is not None:
            return GpgKeyBlock(key, user_ids)
        else:
            return GpgKeyBlock(None, None)

    def add_signature(self, data=None, path=None, pubring=None):
        """
        Adds a key's signature to the public keyring.
        Returns the triple GpgResult(code, stdout, stderr, status, success).
        """
        args = ('--import-options', 'import-minimal', '--import')
        stdin = None
        if data is not None:
            stdin = data
        elif path is not None:
            args.append(path)
        else:
            raise GpgMissingData

        (out, err, status, code) = self._run(stdin=stdin, args=args, pubring=pubring)

        success = False
        for line in status:
            if line[0] == 'IMPORT_OK':
                success = True
                break

        return GpgResult(code, out, err, status, success)

    def remove_signature(self, keyid, pubring=None):
        """
        Removes a signature from the public keyring
        Returns the triple GpgResult(code, stdout, stderr, status, success).
        """
        args = ('--yes', '--delete-key', keyid)
        (out, err,  status, code) = self._run(args=args, pubring=pubring)

        success = code == 0


        return GpgResult(code, out, err, status, success)



    def _run(self, stdin=None, args=None, pubring=None):
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
            raise GpgPathNotInitialisedException

        if pubring is None:
            pubring = self.default_keyring

        in_status_fd, out_status_fd = os.pipe()


        cmd = [
            self.gpg_path,
            '--no-options',
            '--batch',
            '--status-fd', '{0}'.format(out_status_fd),
            '--no-default-keyring',
            '--secret-keyring', pubring + ".secret",
            '--keyring', pubring,
            ]
        if args is not None:
            cmd.extend(args)

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        (output, outerr) = process.communicate(input=stdin)
        code = process.returncode
        os.close(out_status_fd)

        with os.fdopen(in_status_fd, 'r') as f:
            status = [line[len('[GNUPG:] '):].split()
                        for line in f.readlines()]

        return (output, outerr, status, code)

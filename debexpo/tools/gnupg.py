#   gnupg.py — Debexpo gnupg functions
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Serafeim Zanikolas <serzan@hellug.gr>
#               2011 Arno Töll <debian@toell.net>
#               2019 Baptiste Beauplat <lyknode@cilg.org>
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

import logging
import os
import subprocess
import re
import tempfile
from os.path import basename

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from debexpo.tools.proc import debexpo_exec

log = logging.getLogger(__name__)


class ExceptionGnuPG(Exception):
    pass


class ExceptionGnuPGMultipleKeys(ExceptionGnuPG):
    pass


class ExceptionGnuPGPathNotInitialized(ExceptionGnuPG):
    pass


class ExceptionGnuPGNotSignedFile(ExceptionGnuPG):
    pass


class ExceptionGnuPGNoPubKey(ExceptionGnuPG):
    def __init__(self, filename, fingerprint, long_id):
        self.filename = filename
        self.fingerprint = fingerprint
        self.long_id = long_id

    def __str__(self):
        if self.fingerprint:
            return 'Unable to verify file {}. No public key found for key {}' \
                   .format(basename(self.filename), self.fingerprint)
        return 'Unable to verify file {}. No public key found for key {}' \
               .format(basename(self.filename), self.long_id)


class GnuPG():
    def __init__(self):
        """
        Wrapper for certain GPG operations.

        Meant to be instantiated only once.
        """
        self.gpg_path = settings.GPG_PATH
        self.gpg_home = tempfile.TemporaryDirectory()

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

    def get_keys_data(self):
        """
        Returns the key object of the given GPG public key.

        ``fingerprints``
            fingerprints of keys to get data for.

        """

        try:
            (output, status) = self._run(['--list-keys'])
            keys = KeyData.read_from_gpg(output.splitlines())

            return list(keys.values())
        except (AttributeError, IndexError):  # pragma: no cover
            log.error("Failed to extract key id from gpg output: '%s'"
                      % output)

    def verify_sig(self, signed_file):
        """
        Returns the fingerprint that signed the file if the signature is valid.
        Otherwise, throws a ExceptionGnuPG exception.

        ``signed_file``
             path to signed file
        """
        args = ['--verify', signed_file]
        (output, status) = self._run(args)
        output = output.splitlines()

        err_sig_re = re.compile(r'\[GNUPG:\] ERRSIG (?P<long_id>\w+)'
                                r' .* (?P<fingerprint>[\w-]+)$')
        err_sig = list(filter(None, map(err_sig_re.match, output)))

        if err_sig:
            fingerprint = err_sig[0].group('fingerprint')
            long_id = err_sig[0].group('long_id')

            if fingerprint == '-':
                fingerprint = None

            raise ExceptionGnuPGNoPubKey(signed_file, fingerprint, long_id)

        no_data_re = re.compile(r'\[GNUPG:\] NODATA')
        no_data = list(filter(None, map(no_data_re.match,
                                        output)))
        if no_data:
            raise ExceptionGnuPGNotSignedFile(
                f'{os.path.basename(signed_file)}: not a GPG signed file')

        valid_sig_re = re.compile(r'\[GNUPG:\] VALIDSIG .*'
                                  r' (?P<fingerprint>\w+)$')
        valid_sig = list(filter(None, map(valid_sig_re.match, output)))

        if not valid_sig:
            raise ExceptionGnuPG('Unknown GPG error. Output was:'
                                 ' {}'.format(output))

        return valid_sig[0].group('fingerprint')

    def import_key(self, data):
        """
        Add the signature(s) within the provided file to the supplied keyring

        ```data```
            valid PGP public key data suitable for
            keyrings

        Returns gpg output
        """
        args = ['--import-options', 'import-minimal', '--import']

        (output, status) = self._run(args, stdin=data)

        if status and output and len(output.splitlines()) > 0:
            raise ExceptionGnuPG(_('Cannot add key:'
                                 ' {}').format(output.splitlines()[0]))

        return (output, status)

    def _run(self, args, stdin=None):
        """
        Run gpg with the given stdin and arguments and return the output and
        exit status.

        ``stdin``
            Feed gpg with this input to stdin
        ``args``
            a list of strings to be passed as argument(s) to gpg
        ``pubring``
            the path to the public gpg keyring. Note that
            ``pubring + ".secret"`` will be used as the private keyring

        """
        if self.gpg_path is None:
            raise ExceptionGnuPGPathNotInitialized()

        output = None

        env = os.environ.copy()
        env['GNUPGHOME'] = self.gpg_home.name

        cmd = [
            '--batch',
            '--no-auto-check-trustdb',
            '--no-options',
            '--no-permission-warning',
            '--status-fd',
            '1',
            '--no-tty',
            '--quiet',
            '--trust-model', 'always',
            '--with-colons',
            '--with-fingerprint'
            ] + args

        try:
            output = debexpo_exec(self.gpg_path, cmd, env=env,
                                  stderr=subprocess.STDOUT,
                                  input=str(stdin))
        except subprocess.CalledProcessError as e:
            return (e.output, e.returncode)
        except subprocess.TimeoutExpired:
            log.warning('gpg: timeout')
            return ('gpg: timeout', -1)

        return (output, 0)


class KeyData():
    """
    Collects data about a key, parsed from gpg --with-colons --fixed-list-mode
    """
    def __init__(self, fpr, pub):
        self.pub = pub
        self.fpr = fpr
        self.uids = {}
        self.subkeys = {}

    def get_uid(self, uid):
        uidfpr = uid[7]
        self.uids[uidfpr] = res = Uid(self, uid)
        return res

    def get_algo(self):
        return self.pub[3]

    def get_size(self):
        return self.pub[2]

    def add_sub(self, sub, subfpr):
        self.subkeys[subfpr] = sub

    def get_all_uid(self):
        user_ids = []
        for uid_object in self.uids.values():
            uid = uid_object.split()
            user_ids.append((uid['name'], uid['email']))
        return user_ids

    @classmethod
    def read_from_gpg(cls, lines):
        """
        Run the given gpg command and read key and signature data from its
        output
        """
        keys = {}
        pub = None
        sub = None
        cur_key = None
        pub_fpr = None

        for lineno, line in enumerate(lines, start=1):
            if line.startswith("pub:"):
                # Keep track of this pub record, to correlate with the following
                # fpr record
                pub = line.split(":")
                sub = None
                cur_key = None
                pub_fpr = None

            elif line.startswith("fpr:"):
                fpr = line.split(":")[9]
                cur_key = keys.get(pub_fpr, None)

                # Correlate fpr with the previous pub record, and start
                # gathering information for a new key
                if pub:
                    keys[fpr] = cur_key = cls(fpr, pub)
                    pub_fpr = fpr
                    pub = None

                elif sub and cur_key:
                    cur_key.add_sub(sub, fpr)
                    sub = None

                # Internal parsing of GPG. No tests case covering
                # failure for that.
                else:  # pragma: no cover
                    raise Exception(f"gpg:{lineno}: found fpr line with no"
                                    " previous pub line")
            elif line.startswith("uid:"):
                if cur_key is None:  # pragma: no cover
                    raise Exception(f"gpg:{lineno}: found uid line with no "
                                    "previous pub+fpr lines")
                cur_key.get_uid(line.split(":"))

            elif line.startswith("sub:"):
                if cur_key is None:  # pragma: no cover
                    raise Exception(f"gpg:{lineno}: found sub line with no "
                                    "previous pub+fpr lines")
                sub = line.split(":")

        return keys


class Uid():
    """
    Collects data about a key uid, parsed from gpg --with-colons
    --fixed-list-mode
    """
    re_uid = re.compile(r"^(?P<name>.+?)"
                        r"\s*(?:\((?P<comment>.+)\))?"
                        r"\s*(?:<(?P<email>.+)>)?$")

    def __init__(self, key, uid):
        self.key = key
        self.uid = uid
        self.name = uid[9]

    def split(self):
        mo = self.re_uid.match(self.name)
        if not mo:
            return None  # pragma: no cover
        return {
                "name": mo.group("name"),
                "email": mo.group("email"),
                "comment": mo.group("comment"),
        }

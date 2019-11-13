#   gnupg.py — Debexpo gnupg functions
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Serafeim Zanikolas <serzan@hellug.gr>
#               2011 Arno Töll <debian@toell.net>
#               2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from debexpo.keyring.models import Key

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
    def __init__(self, filename, fingerprint):
        self.filename = filename
        self.fingerprint = fingerprint

    def __str__(self):
        return 'Unable to verify file {}. No public key found for key {}' \
               .format(self.filename, self.fingerprint)


class GPGSignedFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.key = None

        fingerprint = self._lookup_fingerprint()

        try:
            self.key = Key.objects.get(fingerprint=fingerprint)
        except Key.DoesNotExist:
            raise ExceptionGnuPGNoPubKey(self.filename, fingerprint)

        self.keyring = VirtualKeyring(self.key.user)
        self.keyring.verify_sig(self.filename)

    def _lookup_fingerprint(self):
        gpg = GnuPG()

        try:
            gpg.verify_sig(self.filename)
        except ExceptionGnuPGNoPubKey as e:
            return e.fingerprint

    def get_key(self):
        return self.key


class VirtualKeyring(object):
    def __init__(self, user=None, key=None):
        self.gpg = GnuPG()

        if user:
            key = Key.objects.get(user=user)
            self.gpg.import_key(key.key)
        elif key:
            self.gpg.import_key(key)
        else:
            raise ValueError('Both user and key cannot be None')

        keys = self.gpg.get_keys_data()

        if (len(keys) > 1):
            raise ExceptionGnuPGMultipleKeys(_('Multiple keys not supported'))

        self.key = keys[0]

    def get_fingerprint(self):
        return self.key.fpr

    def get_algo(self):
        return self.key.get_algo()

    def get_size(self):
        return int(self.key.get_size())

    def get_uids(self):
        return self.key.get_all_uid()

    def verify_sig(self, filename):
        self.gpg.verify_sig(filename)


class GnuPG(object):
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

    def get_keys_data(self, fingerprints=[]):
        """
        Returns the key object of the given GPG public key.

        ``fingerprints``
            fingerprints of keys to get data for.

        """
        try:
            (output, status) = self._run(args=['--list-keys'] + fingerprints)
            keys = KeyData.read_from_gpg(output.splitlines())

            return list(keys.values())
        except (AttributeError, IndexError):  # pragma: no cover
            log.error("Failed to extract key id from gpg output: '%s'"
                      % output)

    def verify_sig(self, signed_file):
        """
        Returns the fingerprint that signed the file if the signature is valid.
        Otherwise, throw a ExceptionGnuPG exception.

        ``signed_file``
             path to signed file
        """
        args = ('--verify', signed_file)
        (output, status) = self._run(args=args)

        output = output.splitlines()
        err_sig_re = re.compile(r'\[GNUPG:\] ERRSIG .* (?P<fingerprint>\w+)$')
        err_sig = list(filter(None, map(err_sig_re.match, output)))
        valid_sig_re = re.compile(r'\[GNUPG:\] VALIDSIG .*'
                                  r' (?P<fingerprint>\w+)$')
        valid_sig = list(filter(None, map(valid_sig_re.match, output)))
        no_data_re = re.compile(r'\[GNUPG:\] NODATA')
        no_data = list(filter(None, map(no_data_re.match,
                                        output)))

        if err_sig:
            raise ExceptionGnuPGNoPubKey(signed_file,
                                         err_sig[0].group('fingerprint'))
        elif no_data:
            raise ExceptionGnuPGNotSignedFile('{}: not a GPG signed'
                                              ' file'.format(signed_file))
        elif not valid_sig:
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

        (output, status) = self._run(args=args, stdin=data)

        if status and output and len(output.splitlines()) > 0:
            raise ExceptionGnuPG(_('Cannot add key:'
                                 ' {}').format(output.splitlines()[0]))

        return (output, status)

    def _run(self, stdin=None, args=None):
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
            self.gpg_path,
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
            ]

        if args is not None:
            cmd.extend(args)

        try:
            output = subprocess.check_output(cmd, env=env,
                                             stderr=subprocess.STDOUT,
                                             input=str(stdin), text=True)
        except subprocess.CalledProcessError as e:
            return (e.output, e.returncode)

        return (output, 0)


class KeyData(object):
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
        res = self.uids.get(uidfpr, None)
        if res is None:
            self.uids[uidfpr] = res = Uid(self, uid)
        return res

    def get_algo(self):
        return self.pub[3]

    def get_size(self):
        return self.pub[2]

    def add_sub(self, sub):
        subfpr = tuple(sub[3:6])
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
        for lineno, line in enumerate(lines, start=1):
            if line.startswith("pub:"):
                # Keep track of this pub record, to correlate with the following
                # fpr record
                pub = line.split(":")
                sub = None
                cur_key = None
            elif line.startswith("fpr:"):
                # Correlate fpr with the previous pub record, and start
                # gathering information for a new key
                if pub is None:
                    if sub is not None:
                        # Skip fingerprints for subkeys
                        continue
                    # Internal parsing of GPG. No tests case covering
                    # failure for that.
                    else:  # pragma: no cover
                        raise Exception("gpg:{}: found fpr line with no" +
                                        " previous pub line".format(lineno))
                fpr = line.split(":")[9]
                cur_key = keys.get(fpr, None)
                if cur_key is None:
                    keys[fpr] = cur_key = cls(fpr, pub)
                pub = None
            elif line.startswith("uid:"):
                if cur_key is None:  # pragma: no cover
                    raise Exception("gpg:{}: found uid line with no previous" +
                                    " pub+fpr lines".format(lineno))
                cur_key.get_uid(line.split(":"))
            elif line.startswith("sub:"):
                if cur_key is None:  # pragma: no cover
                    raise Exception("gpg:{}: found sub line with no previous" +
                                    " pub+fpr lines".format(lineno))
                sub = line.split(":")
                cur_key.add_sub(sub)

        return keys


class Uid(object):
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

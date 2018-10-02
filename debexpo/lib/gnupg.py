# -*- coding: utf-8 -*-
#
#   utils.py — Debexpo utility functions
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
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

import pylons
import re

log = logging.getLogger(__name__)

class GnuPG(object):

    GPG_PATH_NOT_INITIALISED = -1
    INVALID_GNUPG_RUN_INVOCATION = -2

    def __init__(self):
        """
        Wrapper for certain GPG operations.

        Meant to be instantiated only once.
        """
        self.gpg_path = pylons.config['debexpo.gpg_path']
        if self.gpg_path is None:
            log.error('debexpo.gpg_path is not set in configuration file' +
                      ' (or is set to a blank value)')
        elif not os.path.isfile(self.gpg_path):
            log.error('debexpo.gpg_path refers to a non-existent file')
            self.gpg_path = None
        elif not os.access(self.gpg_path, os.X_OK):
            log.error('debexpo.gpg_path refers to a non-executable file')
            self.gpg_path = None
        self.default_keyring = pylons.config['debexpo.gpg_keyring']
        if self.default_keyring is None:
            log.warning('debexpo.gpg_keyring is not set in configuration file' +
                    ' (or is set to a blank value)')

    def is_unusable(self):
        """Returns true if the gpg binary is not installed or not executable."""
        return self.gpg_path is None

    def extract_key_id(self, key):
        """
        Returns the key id only of a given GPG public key, e.g.:

        1024D/355304E4 -> 355304E4

        ``key``
            A public key output as given by gpg(1)
        """
        try:
            r = key.split("/")[1]
            if not r:
                raise AttributeError
            return r
        except (AttributeError, IndexError):
            log.error("Failed to extract key only id from gpg output: '%s'"
                % key)

    def parse_key_id(self, key, email = None):
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
            output = unicode(output, errors='replace')
            keys = KeyData.read_from_gpg(output.splitlines())
            for key in keys.values():
                return key.get_id()
        except (AttributeError, IndexError):
            log.error("Failed to extract key id from gpg output: '%s'"
                       % output)


    def verify_sig(self, signed_file, pubring=None):
        """
        Does the same as verify_sig_full() but is meant as compatibility
        function which returns a boolean only

        """
        (_, status) = self.verify_sig_full(signed_file, pubring)
        return status == 0

    def verify_sig_full(self, signed_file, pubring=None):
        """
        Returns a tuple (file output, return code) if the given GPG-signed file
        can be verified.

        ``signed_file``
             path to signed file
        ``pubring``
             path to public key ring (when not specified, the default GPG
             setting will be used (~/.gnupg/pubring.gpg))
        """
        args = ('--verify', signed_file)
        return self._run(args=args, pubring=pubring)


    def add_signature(self, signature_file, pubring=None):
        """
        Add the signature(s) within the provided file to the supplied keyring

        ```signature_file```
            A file name containing valid PGP public key data suitable for keyrings
        ```pubring```
            A file name pointing to a keyring. May be empty.

        Returns a tuple (file output, return code)
        """
        args = ('--import-options', 'import-minimal', '--import', signature_file)
        return self._run(args=args, pubring=pubring)


    def remove_signature(self, keyid, pubring=None):
        """
        Remove the signature matching the provided keyid from the supplied keyring

        ```keyid```
            The GnuPG keyid to be removed
        ```pubring```
            A file name pointing to a keyring. May be empty.

        Returns a tuple (file output, return code)
        """
        args = ('--yes', '--delete-key', keyid)
        return self._run(args=args, pubring=pubring)


    def _run(self, stdin=None, args=None, pubring=None):
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
            return (None, GnuPG.GPG_PATH_NOT_INITIALISED)

        if pubring is None:
            pubring = self.default_keyring

        cmd = [
            self.gpg_path,
            '--batch',
            '--keyring', pubring,
            '--no-auto-check-trustdb',
            '--no-default-keyring',
            '--no-options',
            '--no-permission-warning',
            '--no-tty',
            '--quiet',
            '--secret-keyring', pubring + ".secret",
            '--trust-model', 'always',
            '--with-colons',
            '--with-fingerprint'
            ]
        if not args is None:
                cmd.extend(args)

        process = subprocess.Popen(cmd,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        output = "\n".join(process.communicate(input=stdin))
        status = process.returncode

        return (output, status)

    def is_signed(self, signed_file):
        """
        Returns true if the given file appears to be GPG signed

        ``signed_file``
            path to a file
        """
        try:
            f = open(signed_file, 'r')
            contents = f.read()
            f.close()
        except:
            log.critical('Could not open %s; continuing' % signed_file)
            return False
        if contents.startswith('-----BEGIN PGP SIGNED MESSAGE-----'):
            return True
        return False


class GPGAlgo(object):
    """
    Static data about GPG PubKey Algo. Extracted from GnuPG source.
    """
    gpg_algo = {
        '1': {'short': 'R', 'long': 'rsa', 'with_size': True},
        '2': {'short': 'r', 'long': 'rsa', 'with_size': True},
        '3': {'short': 's', 'long': 'rsa', 'with_size': True},
        '16': {'short': 'g', 'long': 'elg', 'with_size': True},
        '17': {'short': 'D', 'long': 'dsa', 'with_size': True},
        '18': {'short': 'e', 'long': 'rsa', 'with_size': True},
        '19': {'short': 'E', 'long': 'cv25519', 'with_size': False},
        '20': {'short': 'G', 'long': 'xxx', 'with_size': True},
        '22': {'short': 'E', 'long': 'ed25519', 'with_size': False},
    }

    @classmethod
    def to_short(cls, algo, keysize):
        if algo not in cls.gpg_algo:
            return None
        return '{}{}'.format(keysize, cls.gpg_algo[algo]['short'])

    @classmethod
    def to_long(cls, algo, keysize):
        if algo not in cls.gpg_algo:
            return None
        algo_str = '{}'.format(cls.gpg_algo[algo]['long'])
        if cls.gpg_algo[algo]['with_size']:
            algo_str.append('{}'.format(keysize))


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

    def add_sub(self, sub):
        subfpr = tuple(sub[3:6])
        self.subkeys[subfpr] = sub

    def format_short_fpr(self, fpr):
        return fpr[-8:]

    # Extract an ID of the pub key in its former gpgv1 form:
    # Ex. 1024D/355304E4
    def get_id(self):
        short_id = GPGAlgo.to_short(self.pub[3], self.pub[2])
        short_fpr = self.format_short_fpr(self.pub[4])
        return "{}/{}".format(short_id, short_fpr)

    def keycheck(self):
        return KeycheckKeyResult(self)

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
        cur_uid = None
        for lineno, line in enumerate(lines, start=1):
            if line.startswith("pub:"):
                # Keep track of this pub record, to correlate with the following
                # fpr record
                pub = line.split(":")
                sub = None
                cur_key = None
                cur_uid = None
            elif line.startswith("fpr:"):
                # Correlate fpr with the previous pub record, and start
                # gathering information for a new key
                if pub is None:
                    if sub is not None:
                        # Skip fingerprints for subkeys
                        continue
                    else:
                        raise Exception("gpg:{}: found fpr line with no" +
                                        " previous pub line".format(lineno))
                fpr = line.split(":")[9]
                cur_key = keys.get(fpr, None)
                if cur_key is None:
                    keys[fpr] = cur_key = cls(fpr, pub)
                pub = None
                cur_uid = None
            elif line.startswith("uid:"):
                if cur_key is None:
                    raise Exception("gpg:{}: found uid line with no previous" +
                                    " pub+fpr lines".format(lineno))
                cur_uid = cur_key.get_uid(line.split(":"))
            elif line.startswith("sig:"):
                sig = line.split(":")
                if sig[1] == "%":
                    log.debug("gpg:%s: Invalid signature: <%s>",
                              lineno,
                              line.strip())
                    continue
                if cur_uid is None:
                    raise Exception("gpg:{}: found sig line with no previous" +
                                    " uid line".format(lineno))
                cur_uid.add_sig(sig)
            elif line.startswith("sub:"):
                if cur_key is None:
                    raise Exception("gpg:{}: found sub line with no previous" +
                                    " pub+fpr lines".format(lineno))
                sub = line.split(":")
                cur_key.add_sub(sub)

        return keys


class Uid(object):
    """
    Collects data about a key uid, parsed from gpg --with-colons --fixed-list-mode
    """
    re_uid = re.compile(r"^(?P<name>.+?)\s*(?:\((?P<comment>.+)\))?\s*(?:<(?P<email>.+)>)?$")

    def __init__(self, key, uid):
        self.key = key
        self.uid = uid
        self.name = uid[9]
        self.sigs = {}

    def add_sig(self, sig):
        # FIXME: missing a full fingerprint, we try to index with as much
        # identifying data as possible
        k = tuple(sig[3:6])
        self.sigs[k] = sig

    def split(self):
        mo = self.re_uid.match(self.name)
        if not mo: return None
        return {
                "name": mo.group("name"),
                "email": mo.group("email"),
                "comment": mo.group("comment"),
        }

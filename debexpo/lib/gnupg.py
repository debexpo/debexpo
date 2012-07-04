# -*- coding: utf-8 -*-
#
#   utils.py — Debexpo utility functions
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
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
import re

import pylons

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

    def extract_key_data(self,key,attribute):
        """
        Returns the attribute of a given GPG public key.
        Attribute can be one of "keyid" or "keystrength"
        """
        try:
            if attribute == "keyid":
                r = key.split("/")[1]
            elif attribute == "keystrength":
                r = int(key.split("/")[0][:-1])
            else:
                raise AttributeError
            if not r:
                raise AttributeError
            return r
        except (AttributeError, IndexError):
            log.error("Failed to extract key data from gpg output: '%s'"
                % key)



    def extract_key_id(self, key):
        """
        Returns the key id only of a given GPG public key, e.g.:

        1024D/355304E4 -> 355304E4

        ``key``
            A public key output as given by gpg(1)
        """
        return self.extract_key_data(key,"keyid")

    def extract_key_strength(self, key):
        """
        Returns the key strength only of a given GPG public key, e.g.:

        1024D/355304E4 -> 1024

        ``key``
            A public key output as given by gpg(1)
        """
        return self.extract_key_data(key,"keystrength")

    def parse_key_id(self, key, email = None):
        """
        Returns the key id of the given GPG public key along with a list of user ids.

        ``key``
            ASCII armored GPG public key.

         Sample output to be parsed:

        pub  1024D/355304E4 2005-09-13 Serafeim Zanikolas <serzan@hellug.gr>
        sub  1024g/C082E9B7 2005-09-13 [expires: 2008-09-12]

        """
        try:
            (output, _) = self._run(stdin=key)
            output = unicode(output, errors='replace')
            lines = (output.split('\n'))
            key_id = None
            user_ids = []
            gpg_addr_pattern =  re.compile('(pub\s+\S+\s+\S+\s+|uid\s+)'
                                        '(?P<name>.+)'
                                        '\s+'
                                        '<(?P<email>.+?)>'
                                        '$')

            for line in lines:
                if not key_id and line.startswith('pub'):
                    # get only the 2nd column of the 1st matching line
                    key_id = line.split()[1]
                addr_matcher = gpg_addr_pattern.search(line)
                if addr_matcher is not None:
                    user_ids.append( (addr_matcher.group('name'), addr_matcher.group('email')) )
                if line.startswith('sub'):
                    break

            return (key_id, user_ids)

        except (AttributeError, IndexError):
            log.error("Failed to extract key id from gpg output: '%s'"
                       % output)


    def verify_sig(self, signed_file, pubring=None):
        """
        Does the same as verify_sig_full() but is meant as compatibility
        function which returns a boolean only

        """
        (_, _, status) = self.verify_sig_full(signed_file, pubring)
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
        (raw_out, return_code) = self._run(args=args, pubring=pubring)
        gpg_addr_pattern =  re.compile('"'
                                        '(?P<name>.+)'
                                        '\s+'
                                        '<(?P<email>.+?)>'
                                        '"')
        gpg_key_pattern = re.compile(".*Signature made.*using (?P<key_type>\S+) key ID (?P<key_id>\w+)$")
        
        out = {}
        out['raw'] = raw_out

        user_ids = []
        for line in raw_out.split("\n"):
            # key information
            gpg_key_matcher = gpg_key_pattern.search(line)
            if gpg_key_matcher is not None:
                out['key_type'] = gpg_key_matcher.group('key_type')
                out['key_id'] = gpg_key_matcher.group('key_id')

            # user names and email address
            addr_matcher = gpg_addr_pattern.search(line)
            
            if addr_matcher is not None:
                user_ids.append( (addr_matcher.group('name'), addr_matcher.group('email')) )
        return (out, user_ids, return_code)


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
            '--no-options',
            '--batch',
            '--no-default-keyring',
            '--secret-keyring', pubring + ".secret",
            '--keyring', pubring,
            ]
        if not args is None:
                cmd.extend(args)

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
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

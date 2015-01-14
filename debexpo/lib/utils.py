# -*- coding: utf-8 -*-
#
#   utils.py — Debexpo utility functions
#
#   This file is part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
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
Holds misc utility functions.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import logging
import hashlib
import os

from pylons import config

from debexpo.lib import gnupg

log = logging.getLogger(__name__)

def parse_section(section):
    """
    Works out the component and section from the "Section" field.
    Sections like `python` or `libdevel` are in main.
    Sections with a prefix, separated with a forward-slash also show the component.
    It returns a list of strings in the form [component, section].

    For example, `non-free/python` has component `non-free` and section `python`.

    ``section``
        Section name to parse.
    """
    if '/' in section:
        component, thesection = section.split('/', 1)
        if component not in ("main", "contrib", "non-free"):
            log.warning("Parsing weird component %s, assuming main" % component)
            return 'main', section.replace('/', '_')
        else:
            return [component, thesection]
    else:
        return ['main', section]

def get_package_dir(source):
    """
    Returns the directory name where the package with name supplied as the first argument
    should be installed.

    ``source``
        Source package name to use to work out directory name.
    """
    if source.startswith('lib'):
        return os.path.join(source[:4], source)
    else:
        return os.path.join(source[0], source)

def md5sum(filename):
    """
    Returns the md5sum of a file specified.

    ``filename``
        File name of the file to md5sum.
    """
    try:
        f = file(filename, 'rb')
    except:
        raise AttributeError('Failed to open file %s.' % filename)

    sum = hashlib.md5()
    while True:
        chunk = f.read(10240)
        if not chunk:
            break
        sum.update(chunk)

    f.close()

    return sum.hexdigest()

def random_hash():
    s = os.urandom(20)
    return hash_it(s)

def hash_it(s):
    if type(s) == unicode:
        s = s.encode('utf-8')
    return hashlib.md5(s).hexdigest()

def get_gnupg():
    """
    Returns an instantiated GnuPG object using debexpo's options for the ``gpg`` binary's and keyring's paths.
    """
    return gnupg.GnuPG(config['debexpo.gpg_path'],
                       config['debexpo.gpg_keyring'])

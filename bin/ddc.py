#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   ddc.py — debian-devel-changes mail parser
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
Executable script to parse debian-devel-changes emails and perform
appropriate action.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

from optparse import OptionParser
import ConfigParser
import logging
import logging.config
import os
import sys

log = None

class DdcParser(object):
    """
    Class to handle a package uploaded to Debian.
    """

    def __init__(self, ini, email):
        """
        Object constructor. Sets class fields to sane values.

        ``ini``
            .ini configuration file.

        ``email``
            Email sent to d-d-c.
        """
        self.ini_file = ini
        self.email = email

    def _fail(self, message):
        if log is not None:
            log.critical(message)
        else:
            print >> sys.stderr, message

        sys.exit(1)

    def _setup_logging(self):
        """
        Parse the config file and create the ``log`` object for other methods to log their
        actions.
        """
        global log

        # Parse the ini file to validate it
        parser = ConfigParser.ConfigParser()
        parser.read(self.ini_file)

        # Check for the presence of [loggers] in self.ini_file
        if not parser.has_section('loggers'):
            print >> sys.stderr, 'Config file does not have [loggers] section'
            return

        logging.config.fileConfig(self.ini_file)

        # Use "name.pid" to avoid parser confusions in the logs
        logger_name = '%s.%s' % (__name__, os.getpid())
        log = logging.getLogger(logger_name)

    def _setup(self):
        """
        Set up logging, import pylons/paste/debexpo modules, parse config file and create config
        """
        # Look for ini file
        if not os.path.isfile(self.ini_file):
            self._fail('Cannot find ini file %s' % self.ini_file)

        self._setup_logging()

        # Import debexpo root directory
        sys.path.append(os.path.dirname(self.ini_file))

        # Import debexpo modules
        from paste.deploy import appconfig
        from pylons import config
        from debexpo.config.environment import load_environment

        # Save app config for later
        self.config = config

        # Initialize Pylons app
        conf = appconfig('config:' + options.ini)
        load_environment(conf.global_conf, conf.local_conf)

    def main(self):
        """
        Parse the d-d-c email and take action.
        """
        # Set up
        self._setup()

        if log is not None:
            log.debug('d-d-c parser started with arguments: %s' % sys.argv[1:])

        from debexpo.lib.changes import Changes
        from debexpo.lib.repository import Repository
        from debexpo.lib.plugins import Plugins

        changes = Changes(string=self.email)

        Plugins('post-upload-to-debian', changes, None)

        # Refresh the Sources/Packages files.
        log.debug('Updating Sources and Packages files')
        r = Repository(self.config['debexpo.repository'])
        r.update()

        log.debug('Done')

if __name__ == '__main__':

    parser = OptionParser(usage="%prog -i FILE")
    parser.add_option('-i', '--ini', dest='ini',
                      help='Configuration file to user',
                      metavar='FILE', default=None)
    (options, args) = parser.parse_args()

    if not options.ini:
        parser.print_help()
        sys.exit(0)

    email = sys.stdin.read()

    p = DdcParser(options.ini, email)

    p.main()

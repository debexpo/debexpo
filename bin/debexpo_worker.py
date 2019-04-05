#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#   debexpo_worker.py — Worker task
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2011 Arno Töll <debian@toell.net>
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
Holds the worker task, which cyclically eecutes tasks, defined as cronjob
"""

__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2011 Arno Töll'
__license__ = 'MIT'


import logging
import logging.config
import os
import sys
import time
import ConfigParser
import pylons
import optparse
import signal
import datetime

from paste.deploy import appconfig
from debexpo.config.environment import load_environment

log = None


class Worker(object):
    def __init__(self, pidfile, inifile, daemonize):
        """
        Class constructor. Sets class attributes and then runs the service

        ``pidfile``
            The file name where the worker thread stores its PID file
        ``inifile``
            The configuration file used to setup the worker thread
        ``inifile``
            Whether to go into background
        """

        self.pidfile = pidfile
        self.inifile = os.path.abspath(inifile)
        self.daemonize = daemonize
        self.jobs = {}

    def _daemonize(self):
        """
        Daemonize method. Runs the actual worker thread in the background
        """
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            log.error("%s failed to fork: %s (err %d)" %
                      (__name__, e.strerror, e.errno))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        signal.signal(signal.SIGTERM, self._remove_pid)
        file(self.pidfile, "w+").write("%d\n" % os.getpid())

    def _remove_pid(self, _a, _b):
        """
        Remove the process PID file
        """
        os.remove(self.pidfile)

    def _import_plugin(self, name):
        """
        Imports a module and returns it.
        This is vastly the same piece of code as lib.plugins._import_plugin

        ``name``
            The plugin name to be looked up and imported to the worker task list
        """

        try:
            log.debug('Trying to import cronjob: %s', name)
            mod = __import__(name)
            components = name.split('.')
            for comp in components[1:]:
                    mod = getattr(mod, comp)
            log.debug('Import succeeded.')
            return mod
        except ImportError as e:
            if str(e).startswith('No module named'):
                    log.debug('Import failed - module not found: %s', e)
            else:
                    log.warn('Import of module "%s" failed with error: %s',
                             name, e)
        return None

    def _load_jobs(self):
        """
        Tries to load configured cronjobs. This method roughly works the same
        way, as does the equivalent method in the plugins code.
        """

        if 'debexpo.cronjobs' not in pylons.config:
            log.error("debexpo.cronjobs it not set - doing nothing?")
            sys.exit(1)

        for plugin in pylons.config['debexpo.cronjobs'].split(" "):
            module = None
            if 'debexpo.cronjobdir' in pylons.config:
                sys.path.append(pylons.config['debexpo.cronjobdir'])
                module = self._import_plugin(plugin)
                if module is not None:
                        log.debug('Found cronjob in debexpo.cronjobdir')

            if module is None:
                    name = 'debexpo.cronjobs.%s' % plugin
                    module = self._import_plugin(name)

            if not module:
                log.warning("Cronjob %s was configured, but not found" %
                            (plugin))
                continue

            if hasattr(module, 'cronjob') and hasattr(module, 'schedule'):
                    self.jobs[plugin] = {
                        'module': getattr(module, 'cronjob')(
                            parent=self, config=pylons.config, log=log),
                        'schedule': getattr(module, 'schedule'),
                        'last_run': datetime.datetime(year=1970, month=1, day=1)
                    }
            else:
                    log.debug("Cronjob %s seems invalid" % (plugin))

    def _setup(self):
        """
        Sets up the worker task. Setup logging, Pylons globals and so on
        """

        global log
        config = ConfigParser.ConfigParser()
        config.read(self.inifile)

        if not config.has_section('loggers'):
            # Sorry, the logger has not been set up yet
            print('Config file does not have [loggers] section')
            sys.exit(1)

        logging.config.fileConfig(self.inifile)
        logger_name = 'debexpo.worker'
        log = logging.getLogger(logger_name)

        sys.path.append(os.path.dirname(self.inifile))
        conf = appconfig('config:' + self.inifile)
        pylons.config = load_environment(conf.global_conf, conf.local_conf)

    def run(self):
        """
        Run the event loop.
        This method never returns
        """

        self._setup()
        if os.path.exists(self.pidfile):
            try:
                read_pid = file(self.pidfile, 'r')
                pid = read_pid.readline().strip()
                read_pid.close()
            except Exception:
                pid = None
        else:
            pid = None

        if pid:
            log.error("Refusing to start - is another instance with PID "
                      "%s running?" % (pid))
            sys.exit(1)

        if self.daemonize:
            log.debug("Go into background now")
            self._daemonize()
        log.debug("Loading jobs")
        self._load_jobs()
        delay = int(pylons.config['debexpo.cronjob_delay'])

        while(True):
            for job in self.jobs:
                if ((datetime.datetime.now() - self.jobs[job]['last_run']) >=
                        self.jobs[job]['schedule']):
                    log.debug("Run job %s" % (job))
                    self.jobs[job]['module'].invoke()
                    self.jobs[job]['last_run'] = datetime.datetime.now()
                    log.debug("Job %s complete" % (job))
            time.sleep(delay)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ini", dest="ini",
                      help="path to application ini file", metavar="FILE")
    parser.add_option("-p", "--pid-file", dest="pid",
                      help="path where the PID file is stored", metavar="FILE")
    parser.add_option("-d", "--daemonize", dest="daemonize",
                      action='store_true', help="go into background")

    (options, args) = parser.parse_args()
    if not options.pid or not options.ini:
        parser.print_help()
        sys.exit(0)

    worker = Worker(options.pid, options.ini, options.daemonize)
    worker.run()

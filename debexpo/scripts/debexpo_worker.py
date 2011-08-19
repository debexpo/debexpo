#! /usr/bin/python
# -*- coding: utf-8 -*-
#
#   debexpo_worker.py — Worker task
#
#   This file is part of debexpo - http://debexpo.workaround.org
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
import atexit
import sys
import time
import ConfigParser
import pylons

from paste.deploy import appconfig
from debexpo.config.environment import load_environment

log = None

class Worker(object):
	def __init__(self, pidfile, inifile):
		"""
		Class constructor. Sets class attributes and then runs the service
		"""

		self.pidfile = pidfile
		self.inifile = os.path.abspath(inifile)
		self.jobs = {}


	def _daemonize(self):
		try:
			pid = os.fork()
			if pid > 0:
				sys.exit(0)
		except OSError as e:
			log.error( "%s failed to fork: %s (err %d)" % (__name__, e.strerror, e.errno))
			sys.exit(1)

		os.chdir("/")
		os.setsid()
		os.umask(0)

		atexit.register(self._remove_pid)
		file(self.pidfile, "w+").write( "%d\n" % os.getpid())

	def _remove_pid(self):
		os.remove(self.pidfile)


	def _import_plugin(self, name):
		"""
		Imports a module and returns it.
		This is vastly the same piece of code as lib.plugins._import_plugin
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
			if e.message.startswith('No module named'):
					log.debug('Import failed - module not found: %s', e)
			else:
					log.warn('Import of module "%s" failed with error: %s', name, e)
		return None

	def _load_jobs(self):
		if not 'debexpo.cronjobs' in pylons.config:
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
					log.warning("Cronjob %s was configured, but not found" % (plugin))
					continue

			if hasattr(module, 'cronjob') and hasattr(module, 'schedule'):
					self.jobs[module] = {
							'module': getattr(module, 'cronjob')(parent=self, config=pylons.config),
							'schedule': getattr(module, 'schedule')
					}
			else:
					log.debug("Cronjob %s seems invalid" % (plugin))

	def _setup(self):
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
		self._setup()
		#self._daemonize()
		self._load_jobs()

		while(True):
			for job in self.jobs:
				log.debug("Run job %s" % (job))
			time.sleep(5)

if __name__ == '__main__':
	worker = Worker('/tmp/pid.file', '/home/at/debexpo/development-arno.ini')
	worker.run()

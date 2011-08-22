# -*- coding: utf-8 -*-
#
#   plugins.py — Plugin loader
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
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
Holds the plugin loader.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

from debian import deb822
import logging
import os
import tempfile
import shutil
import sys
import pylons

log = logging.getLogger(__name__)

# Different plugin stages and their options.
plugin_stages = {
    'post-upload' : {
        'extract' : False,
    },
    'qa' : {
        'extract' : True,
    },
    'post-upload-to-debian' : {
        'extract' : False,
    },
    'post-successful-upload' : {
        'extract' : False,
    },
}

class Plugins(object):

    def __init__(self, type, changes, changes_file, **kw):
        """
        Class constructor. Sets class attributes and then runs the plugins.

        ``type``
            Type of plugins to run. (E.g. "post-upload")

        ``changes``
            Changes class for the package to test.

        ``changes_file``
            Name of the changes file.

        ``kw``
            Extra information for plugins to have.
        """
        self.config = pylons.config
        self.type = type.replace('-', '_')
        self.changes = changes
        self.changes_file = changes_file
        self.result = None
        self.tempdir = None
        self.kw = kw

        # Run the plugins.
        if type in plugin_stages:
            self.conf = plugin_stages[type]
            log.debug('Running plugins of type: %s' % type)
            self.result = self._run_plugins()

    def _import_plugin(self, name):
        """
        Imports a module and returns it.

        This method was stolen from:
            http://docs.python.org/lib/built-in-funcs.html

        ``name``
            Module to import.
        """
        try:
            log.debug('Trying to import plugin: %s', name)
            mod = __import__(name)
            components = name.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
            log.debug('Import succeeded.')
            return mod
        except ImportError, e:
            if e.message.startswith('No module named'):
                # Not fatal: the plugin module was not found at this location
                # (might be okay because plugins are looked for in several locations)
                log.debug('Import failed - module not found: %s', e)
            else:
                # The module was found but failed to import for other reasons.
                # It's worth looking into why importing failed.
                log.warn('Import of module "%s" failed with error: %s', name, e)
            return None

    def _extract(self):
        """
        Copy the files to a temporary directory and run dpkg-source -x on the dsc file
        to extract them.
        """
        log.debug('Copying files to a temp directory to run dpkg-source -x on the dsc file')
        self.tempdir = tempfile.mkdtemp()
        log.debug('Temp dir is: %s', self.tempdir)
        for filename in self.changes.get_files():
            log.debug('Copying: %s', filename)
            shutil.copy(os.path.join(self.config['debexpo.upload.incoming'], filename), self.tempdir)

        # If the original tarball was pulled from Debian or from the repository, that
        # also needs to be copied into this directory.
        dsc = deb822.Dsc(file(self.changes.get_dsc()))
        for item in dsc['Files']:
            if item['name'] not in self.changes.get_files():
                src_file = os.path.join(self.config['debexpo.upload.incoming'], item['name'])
                if os.path.exists(src_file):
                    shutil.copy(src_file, self.tempdir)
                else:
                    log.critical("Trying to copy non-existing file %s" % (src_file))

        shutil.copy(os.path.join(self.config['debexpo.upload.incoming'], self.changes_file), self.tempdir)

        self.oldcurdir = os.path.abspath(os.path.curdir)
        os.chdir(self.tempdir)

        os.system('dpkg-source -x %s extracted' % self.changes.get_dsc())

    def _cleanup(self):
        """
        Remove the previously-created temporary directory and chdir back to where the importer
        was.
        """
        if self.tempdir is not None:
            shutil.rmtree(self.tempdir)
            os.chdir(self.oldcurdir)

    def _run_plugins(self):
        """
        Look in the config file and run the plugins.
        """
        key = 'debexpo.plugins.' + self.type
        log.debug("Getting plugins with key (repr): %s", repr(key))
        plugins = self.config.get(key)
        log.debug("Using these plugins: %s", plugins)
        result = []

        if not plugins:
            log.debug("Returning result: %s", result)
            return result

        # Look at whether the plugins need extracting.
        if 'extract' in self.conf and self.conf['extract']:
            log.debug('Extracting package for plugins')
            self._extract()

        # Run each plugin.
        for plugin in plugins.split(' '):
            log.debug('Running %s plugin' % plugin)
            module = None
            if self.config.get('debexpo.plugindir') != '':
                # First try in the user-defined plugindir
                sys.path.append(self.config['debexpo.plugindir'])
                module = self._import_plugin(plugin)
                if module is not None:
                    log.debug('Found plugin in debexpo.plugin_dir')

            if module is None:
                # Try in debexpo.plugins
                name = 'debexpo.plugins.%s' % plugin
                module = self._import_plugin(name)

            # The 'plugin' object points to the class containing the actual plugin/test
            if hasattr(module, 'plugin'):
                p = getattr(module, 'plugin')(name=plugin, changes=self.changes, \
                    changes_file=self.changes_file, tempdir=self.tempdir, \
                    outcomes=getattr(module, 'outcomes'))

                for item in self.kw:
                    setattr(p, item, self.kw[item])

                result.extend(p.run())

        if self.conf['extract']:
            self._cleanup()

        return result

    def stop(self):
        """
        Returns whether the importer should stop.
        """
        for result in self.result:
            if result.stop():
                return True

        return False

# -*- coding: utf-8 -*-
#
#   py.template - template for new .py files
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste BEAUPLAT <lyknode@cilg.org>
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

__author__ = 'Baptiste BEAUPLAT'
__copyright__ = 'Copyright © 2019 Baptiste BEAUPLAT'
__license__ = 'MIT'

from logging import getLogger

from debexpo.tests import TestController
from debexpo.model import meta
from pylons import config


class TestCronjob(TestController):
    def __init__(self, *args, **kargs):
        TestController.__init__(self, *args, **kargs)
        self.db = meta.session
        self.config = config
        self.log = getLogger(__name__)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _setup_plugin(self, plugin, run_setup=True):
        # Dynamically import plugin module
        module = __import__('debexpo.cronjobs.{}'.format(plugin))
        module = getattr(module, 'cronjobs')
        module = getattr(module, plugin)
        self.assertTrue(module is not None)

        # Retrive class name
        module = getattr(module, 'cronjob')
        self.assertTrue(module is not None)

        # Instanciate the cronjob class
        self.plugin = module(parent=self, config=self.config, log=self.log)

        if run_setup:
            self.plugin.setup()

    def _invoke_plugin(self):
        self.plugin.invoke()

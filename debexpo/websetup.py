# -*- coding: utf-8 -*-
#
#   websetup.py — Setup the debexpo application
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
Setup the debexpo application.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import logging
import os

from paste.deploy import appconfig
import pylons.test

from debexpo.config.environment import load_environment
from debexpo.model import import_all_models
from debexpo.model import meta

import debexpo.model.data_store
import debexpo.model.user_countries

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """
    Run when debexpo is being set up, when ``paster setup-app`` is executed and shouldn't
    be called directly.

    ``command``
        Pointer to the setup function.

    ``filename``
        File used for configuration. E.g. `development.ini`.

    ``section``
        Section in the config file; usually `app:main`.

    ``vars``
        Extra variables passed to the setup.
    """

    conf = appconfig('config:' + filename)

    if not pylons.test.pylonsapp:
        config = load_environment(conf.global_conf, conf.local_conf)
    else:
        config = pylons.test.pylonsapp.config

    log.info('Creating database tables')
    import_all_models()
    meta.metadata.create_all(bind=meta.engine)
    log.info('Successfully setup database tables')

    if not os.path.isdir(config['debexpo.upload.incoming']):
        log.info('Creating incoming directory')
        os.mkdir(config['debexpo.upload.incoming'])
    else:
        log.info('Incoming directory already exists')

    if not os.path.isdir(config['debexpo.repository']):
        log.info('Creating repository directory')
        os.mkdir(config['debexpo.repository'])
    else:
        log.info('Repository directory already exists')

    log.info('Making sure all ISO countries are in the database')
    debexpo.model.user_countries.create_iso_countries()

    log.info('Making sure all tags do exist')
    debexpo.model.sponsor_metrics.create_tags()

    log.info('Import data store pre-existing data')
    debexpo.model.data_store.fill_data_store()

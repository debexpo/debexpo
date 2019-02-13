#! /usr/bin/env python

import os
import logging.config
from paste.deploy import loadapp

# "cd" into the code root
os.chdir('/var/www/debexpo')

logging.config.fileConfig('/var/www/debexpo/live.ini')

# Load the Pylons application
application = loadapp('config:/var/www/debexpo/live.ini')

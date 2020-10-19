#   prod.py - Django settings for debexpo project in production environment
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2020 Baptiste Beauplat <lyknode@cilg.org>
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

from .common import *  # noqa
from os import path, getenv

# Read secretkey from file
try:
    with open(path.join(path.dirname(path.abspath(__file__)),
                        'secretkey')) as f:
        secret_key = f.read().strip()
except IOError as e:
    raise Exception('Could not read secret key: {}'.format(e))

if len(secret_key) < 64:
    raise Exception('Secret key too weak. Must be at least 64 char.')

# Read redis passphrase from file
try:
    with open(path.join(path.dirname(path.abspath(__file__)),
                        'redis-password')) as f:
        redis_password = f.read().strip()
except IOError as e:
    raise Exception('Could not read redis password: {}'.format(e))

SECRET_KEY = secret_key
ALLOWED_HOSTS = ['mentors.debian.net']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'debexpo_live'
    }
}

# Debexpo settings
SITE_NAME = 'mentors.debian.net'
SITE_TITLE = 'Mentors'

# Base url used to craft links for non-web tasks (importer)
SITE_URL = 'https://mentors.debian.net'

HOSTING_URL = 'https://www.wavecon.de/'
HOSTING = 'Wavecon'

# Spool settings
UPLOAD_SPOOL = '/var/spool/debexpo'

# Repository
REPOSITORY = '/var/lib/debexpo/repository'

# Git storage (comment to disable)
GIT_STORAGE = '/var/lib/debexpo/git'

# Email settings
# https://docs.djangoproject.com/en/2.2/ref/settings/#email

SUPPORT_EMAIL = 'support@mentors.debian.net'
DEFAULT_FROM_EMAIL = 'mentors.debian.net <support@mentors.debian.net>'
DEFAULT_BOUNCE_EMAIL = 'bounce@mentors.debian.net'
COMMENTS_FROM_EMAIL = 'mentors.debian.net <no-reply@mentors.debian.net>'

# Celery redis connexion
CELERY_BROKER_URL = f'redis://:{redis_password}@localhost:6379'
CELERY_RESULT_BACKEND = f'redis://:{redis_password}@localhost:6379'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://:{redis_password}@127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'debexpo': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
            'level': getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# Enable spam detection
REGISTRATION_SPAM_DETECTION = True

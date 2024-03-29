#   develop.py - Django settings for debexpo project in developement mode
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019 Baptiste Beauplat <lyknode@cilg.org>
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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'DoNotUseThisKeyInProductionEnvironment'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db.sqlite3'),  # noqa: F405
    }
}

# Base url used to craft links for non-web tasks (importer)
SITE_URL = 'http://localhost:8000'

# Email settings
# https://docs.djangoproject.com/en/2.2/ref/settings/#email

SUPPORT_EMAIL = 'support@example.org'
DEFAULT_FROM_EMAIL = 'debexpo <support@example.org>'
DEFAULT_BOUNCE_EMAIL = 'bounce@example.org'
COMMENTS_FROM_EMAIL = 'debexpo <no-reply@example.org>'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = path.join(BASE_DIR, 'data', 'mbox')  # noqa: F405

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
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'level': getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# Spool settings
UPLOAD_SPOOL = path.join(BASE_DIR, 'data', 'spool')  # noqa: F405

# Repository
REPOSITORY = path.join(BASE_DIR, 'data', 'repository')  # noqa: F405

# Git storage
GIT_STORAGE = path.join(BASE_DIR, 'data', 'git')  # noqa: F405

# Don't enforce newer upload checks on tests by default
CHECK_NEWER_UPLOAD = False

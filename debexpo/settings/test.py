#   test.py - Django settings for debexpo project in tests
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

from .common import *  # noqa
from os import path

# Build paths inside the project like this: path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(
    path.dirname(path.dirname(path.abspath(__file__)))
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'DoNotUseThisKeyInProductionEnvironment'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'testing.sqlite3'),
    }
}

# Email settings
# https://docs.djangoproject.com/en/2.2/ref/settings/#email

DEFAULT_FROM_EMAIL = 'debexpo <support@example.org>'
DEFAULT_BOUNCE_EMAIL = 'bounce@example.org'

# Repository location
REPOSITORY = '/tmp/debexpo/repository'

# Git storage location
GIT_STORAGE = '/tmp/debexpo/git'

# Use fakeredis for testing
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "REDIS_CLIENT_CLASS": "fakeredis.FakeStrictRedis",
        }
    }
}

DJANGO_REDIS_CONNECTION_FACTORY = "tests.functional.importer." \
    "FakeConnectionFactory"

# Don't use a worker for testing
CELERY_TASK_ALWAYS_EAGER = True

# Bug plugin settings
BUGS_REPORT_NOT_OPEN = False

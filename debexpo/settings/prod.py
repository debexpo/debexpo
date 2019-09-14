"""
Django settings for debexpo project in production environment.
"""

from .common import *  # noqa
from os import path

DEBEXPO_CONF_DIR = '/etc/debexpo'

try:
    with open(path.join(DEBEXPO_CONF_DIR, 'secretkey')) as f:
        secret_key = f.read().strip()
except IOError as e:
    raise Exception('Could not read secret key: {}'.format(e))

if len(secret_key) < 64:
    raise Exception('Secret key too weak. Must be at least 64 char.')

SECRET_KEY = secret_key
DEBUG = False
ALLOWED_HOSTS = ['mentors.debian.net']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db.sqlite3'),  # noqa: F405
    }
}

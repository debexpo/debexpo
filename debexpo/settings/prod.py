"""
Django settings for debexpo project in production environment.
"""

from .common import *  # noqa
from os import path

DEBEXPO_CONF_DIR = '/etc/debexpo'

with open(path.join(DEBEXPO_CONF_DIR, 'secretkey')) as f:
    secret_key = f.read().strip()

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

"""
Django settings for debexpo project in developement mode.
"""

from .common import *  # noqa
from os import path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'DoNotUseThisKeyInProductionEnvironment'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db.sqlite3'),  # noqa: F405
    }
}

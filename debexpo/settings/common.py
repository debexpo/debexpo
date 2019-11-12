#   common.py - Django settings for debexpo project, common settings
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

from os import path

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(
    path.dirname(path.dirname(path.abspath(__file__)))
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debexpo.base',
    'debexpo.accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'debexpo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'tests/unit/tools/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LANGUAGES = [
  ('en', _('English')),
  ('fr', _('French')),
]

LOCALE_PATHS = [
    path.join(BASE_DIR, 'debexpo', 'locale')
]

WSGI_APPLICATION = 'debexpo.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# Password hashes (read bcrypt and md5, update/create to bcrypt)
# https://docs.djangoproject.com/en/2.2/topics/auth/passwords/

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)

# Debexpo common settings
LOGO = '/img/debexpo-logo.png'
SITE_NAME = 'debexpo'
SITE_TITLE = 'Debexpo'
TAGLINE = _('Helps you get your packages into Debian')
VCS_BROWSER = 'https://salsa.debian.org/mentors.debian.net-team/debexpo'

# SMTP and NNTP settings
SMTP_SERVER = 'localhost'
SMTP_PORT = 25
# SMTP_USERNAME = 'foo'
# SMTP_PASSWORD = 'CHANGEME'

NNTP_SERVER = 'news.gmane.org'

# Debexpo User model
AUTH_USER_MODEL = 'accounts.User'

# GPG settings
GPG_PATH = '/usr/bin/gpg'

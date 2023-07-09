#   common.py - Django settings for debexpo project, common settings
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

from os import path

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(
    path.dirname(path.dirname(path.abspath(__file__)))
)

# Application definition

INSTALLED_APPS = [
    'debexpo.override',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'debexpo.base',
    'debexpo.accounts',
    'debexpo.keyring',
    'debexpo.packages',
    'debexpo.comments',
    'debexpo.importer',
    'debexpo.repository',
    'debexpo.plugins',
    'debexpo.bugs',
    'debexpo.nntp',
    'rest_framework',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debexpo.tools.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'debexpo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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
  ('pt-br', _('Portuguese (Brazil)')),
]

LOCALE_PATHS = [
    path.join(BASE_DIR, 'debexpo', 'locale')
]

WSGI_APPLICATION = 'debexpo.wsgi.application'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


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
STATIC_ROOT = path.join(BASE_DIR, 'static')

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

NNTP_SERVER = 'news.gmane.io'

# Debexpo User model
AUTH_USER_MODEL = 'accounts.User'

# GPG settings
GPG_PATH = '/usr/bin/gpg'

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django'
CELERY_BEAT_SCHEDULE = {
    'remove-old-uploads': {
        'task': 'debexpo.packages.tasks.remove_old_uploads',
        'schedule': 60 * 10,  # Every 10 minutes
    },
    'cleanup-accounts': {
        'task': 'debexpo.accounts.tasks.CleanupAccounts',
        'schedule': 60 * 60,  # Every hours
    },
    'importer': {
        'task': 'debexpo.importer.tasks.importer',
        'schedule': 60 * 15,  # Every 15 minutes
    },
    'remove-uploaded-packages': {
        'task': 'debexpo.packages.tasks.remove_uploaded_packages',
        'schedule': 60 * 10,  # Every 10 minutes
    },
}

# Account registration expiration
REGISTRATION_EXPIRATION_DAYS = 7

# Email update token expiration (2 days to get at the very least 24h)
EMAIL_CHANGE_TIMEOUT_DAYS = 2

# Plugins to load
IMPORTER_PLUGINS = (
    ('debexpo.plugins.distribution', 'PluginDistribution',),
    ('debexpo.plugins.buildsystem', 'PluginBuildSystem',),
    ('debexpo.plugins.watch-file', 'PluginWatchFile',),
    ('debexpo.plugins.native', 'PluginNative',),
    ('debexpo.plugins.maintaineremail', 'PluginMaintainerEmail',),
    ('debexpo.plugins.lintian', 'PluginLintian',),
    ('debexpo.plugins.diffclean', 'PluginDiffClean',),
    ('debexpo.plugins.closedbugs', 'PluginClosedBugs'),
    ('debexpo.plugins.controlfields', 'PluginControlFields',),
    ('debexpo.plugins.debianqa', 'PluginDebianQA',),
    ('debexpo.plugins.rfs', 'PluginRFS',),
)

# Debian Archive access
DEBIAN_ARCHIVE_URL = 'https://deb.debian.org/debian'
LIMIT_SIZE_DOWNLOAD = 100 * 1024 * 1024

# Bug plugin settings
BUGS_REPORT_NOT_OPEN = True

# Debian tracker access
TRACKER_URL = 'https://tracker.debian.org'
FTP_MASTER_NEW_PACKAGES_URL = 'https://ftp-master.debian.org/new.822'
FTP_MASTER_API_URL = 'https://api.ftp-master.debian.org'

# Cleanup package older than NN weeks
MAX_AGE_UPLOAD_WEEKS = 20

# Cleanup incoming queue
QUEUE_EXPIRED_TIME = 6 * 60 * 60  # File TTL is 6 hours

# API settings
REST_FRAMEWORK = {
    # Filtering
    'DEFAULT_FILTER_BACKENDS':
        ('django_filters.rest_framework.DjangoFilterBackend',),

    # Versioning
    'DEFAULT_VERSIONING_CLASS':
        'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': '1',
    'ALLOWED_VERSIONS': ('1',),

    # Rate Limiting
    'DEFAULT_THROTTLE_CLASSES': (
            'rest_framework.throttling.AnonRateThrottle',
        ),
    'DEFAULT_THROTTLE_RATES': {
            'anon': '200/day',  # Approximatively 2 request every 15 minutes
        },
}

# Spam detection
REGISTRATION_SPAM_DETECTION = False

# Time between GET and POST of the registration form
REGISTRATION_MIN_ELAPSED = 3

# How any time an IP can register an account (currently per day)
REGISTRATION_PER_IP = 5

# Forget the IP after 1 day (set to 0 to disable spam detection)
REGISTRATION_CACHE_TIMEOUT = 1 * 24 * 3600

# Timeout for processes (10 minutes by default, 30 minutes for lintian)
SUBPROCESS_TIMEOUT = 10 * 60
SUBPROCESS_TIMEOUT_LINTIAN = 30 * 60

# Default settings for models
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Distro-info vendor info
DISTRO_INFO_VENDOR = 'debian'
DISTRIBUTION_SUFFIX = (
    '-backports',
    '-backports-sloppy',
    '-security',
    '-updates',
    '-proposed-updates',
)
STATIC_SUITES = (
    'sid',
    'experimental',
)
SUITE_ALIASES = {
    'oldstable': None,
    'stable': None,
    'testing': None,
    'unstable': None,
    'UNRELEASED': 'sid',
}
DISTRIBUTION_COMPONENTS = (
    'main',
    'contrib',
    'non-free',
    'non-free-firmware',
)

"""
Django settings for testP project.

Generated by 'django-admin startproject' using Django 1.10.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

import dj_database_url

from .hackathon_variables import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)

environ.Env.read_env()

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = [
    'my.ugahacks.com',
    'ugahacks.com',
    '5.ugahacks.com',
    'localhost',
    '5.localhost',
    '127.0.0.1',
    '0.0.0.0',
    '165.227.125.129',
    '192.168.0.12',
    '192.168.1.18',  # kane
    'acc3e81f.ngrok.io'
]

# Application definition
INSTALLED_APPS = [
    'jet',
    'jet.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'form_utils',
    'bootstrap3',
    'django_tables2',
    'organizers',
    'checkin',
    'user',
    'applications',
    'teams',
    'stats',
    'storages',
    'meals',
    # 'judging',
    'workshops',
    'archives',
    'crispy_forms',
    'sponsors',
    'points',
    'scanning',
    'django_hosts',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

if BAGGAGE_ENABLED:
    INSTALLED_APPS.append('baggage')

if REIMBURSEMENT_ENABLED:
    INSTALLED_APPS.append('reimbursement')

if HARDWARE_ENABLED:
    INSTALLED_APPS.append('hardware')

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',  # This MUST be first

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django_hosts.middleware.HostsResponseMiddleware'  # This MUST be last
]

ROOT_HOSTCONF = 'app.hosts'
DEFAULT_HOST = 'my'

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['app/templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'app.utils.hackathon_vars_processor'

            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases


if DEBUG == True:
    DATABASES = {
        'default': {
            'CONN_MAX_AGE': 0,
            'ENGINE': 'django.db.backends.sqlite3',
            'HOST': 'localhost',
            'NAME': 'project.db',
            'PASSWORD': '',
            'PORT': '',
            'USER': ''
        }
    }

else:

    if os.environ.get('DATABASE_URL', None):
        DATABASES['default'] = dj_database_url.config(
            conn_max_age=600,
            ssl_require=os.environ.get('DATABASE_SECURE', 'true').lower() != 'false',
        )

    if os.environ.get('PG_PWD', None):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': os.environ.get('PG_NAME', 'ugahacksfive'),
                'USER': os.environ.get('PG_USER', 'ugahacksfiveuser'),
                'PASSWORD': os.environ.get('PG_PWD'),
                'HOST': os.environ.get('PG_HOST', 'localhost'),
                'PORT': '5432',
            }
        }

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Logging config to send logs to email automatically
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'admin_email': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'app.log.HackathonDevEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'level': 'ERROR',
            'handlers': ['admin_email'],
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + '/staticfiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, os.path.join('app', "static")),
]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

#  File upload configuration
MEDIA_ROOT = 'files'
MEDIA_URL = '/files/'

if os.environ.get('DROPBOX_OAUTH2_TOKEN', False):
    DEFAULT_FILE_STORAGE = 'storages.backends.dropbox.DropBoxStorage'
    DROPBOX_OAUTH2_TOKEN = os.environ.get('DROPBOX_OAUTH2_TOKEN', False)
    DROPBOX_ROOT_PATH = HACKATHON_DOMAIN.replace('.', '_')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'no-reply@ugahacks.com'
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'UGAHacks Team <no-reply@ugahacks.com>'

# Jet configs
JET_SIDE_MENU_COMPACT = True
JET_INDEX_DASHBOARD = 'app.jet_dashboard.CustomIndexDashboard'

# Set up custom auth
AUTH_USER_MODEL = 'user.User'
LOGIN_URL = 'account_login'
PASSWORD_RESET_TIMEOUT_DAYS = 1

BOOTSTRAP3 = {
    # Don't normally want placeholders.
    'set_placeholder': False,
    'required_css_class': 'required',
}

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': os.path.join(BASE_DIR, 'cache'),
        }
    }

OAUTH_PROVIDERS = {
    'mlh': {
        'auth_url': 'https://my.mlh.io/oauth/authorize',
        'token_url': 'https://my.mlh.io/oauth/token',
        'id': os.environ.get('MLH_CLIENT_SECRET', '').split('@')[0],
        'secret': os.environ.get('MLH_CLIENT_SECRET', '@').split('@')[1],
        'scope': 'email+event+education+phone_number',
        'user_url': 'https://my.mlh.io/api/v2/user.json'

    }
}

# Add domain to allowed hosts
ALLOWED_HOSTS.append(HACKATHON_DOMAIN)

# Deployment configurations for proxy pass and csrf
CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Maximum file upload size for forms
MAX_UPLOAD_SIZE = 5242880

MEALS_TOKEN = os.environ.get('MEALS_TOKEN', None)

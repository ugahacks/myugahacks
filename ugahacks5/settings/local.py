import os
from ugahacks5.settings.base import *

DEBUG = True

INSTALLED_APPS += [
    'debug_toolbar', # and other apps for local development
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'souqwp5carc13c(e@&&1hu2bxdz!&0c59hqrpg(ujw_9u723h)'



ALLOWED_HOSTS = ['*']


INTERNAL_IPS = ['127.0.0.1']

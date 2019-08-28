# noinspection PyUnresolvedReferences
from .base import *

DEBUG = True

JQUERY_URL = '//cdn.bootcss.com/jquery/2.1.4/jquery.min.js'

# To set development server ip and port
DEV_SERVER = '0.0.0.0:8000'

INSTALLED_APPS += [
]

NOT_CODE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'utils',
    'account',
]

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, '../db.sqlite3'),
#     }
# }


MIDDLEWARE += [
]

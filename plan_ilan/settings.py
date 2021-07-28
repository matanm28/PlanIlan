"""
Django settings for plan_ilan project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import json
import os
import socket
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0p!a&2d!ui+clgkdpgj7umd+0$k)m+#@dqacj7)=r)tqyy@_#t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['plan-ilan-env.eba-aq8y523e.eu-central-1.elasticbeanstalk.com',
                 '127.0.0.1', '52.58.94.40', '172.22.32.1','172.31.24.250']

# Application definition

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

INSTALLED_APPS = [
    'plan_ilan.apps.web_site',
    'plan_ilan.apps.timetable_generator',
    'django_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'django_admin_multiple_choice_list_filter',
    'polymorphic',
    'rest_framework',
    'crispy_forms',
    'debug_toolbar',
    'storages',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'plan_ilan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR]
        ,
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

WSGI_APPLICATION = 'plan_ilan.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DEVELOPMENT = False
IS_MATAN_MACHINE = socket.gethostname() == 'MAMALKA-FSYX3'
DB_HOST = 'LOCAL' if DEVELOPMENT and IS_MATAN_MACHINE else 'AWS'
db_information = dict(os.environ)
db_data = db_information
db_data_file_name = 'tmp/db_data.json'
if os.path.exists(db_data_file_name):
    with open(db_data_file_name, 'r') as json_file:
        db_json = json.load(json_file)
        db_data = db_json[DB_HOST]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'CONN_MAX_AGE': 3600,
        'NAME': db_data['DB_NAME'],
        'USER': db_data['DB_USER_NAME'],
        'PASSWORD': db_data['DB_USER_PASSWORD'],
        'HOST': db_data['DB_HOST_NAME'],
        'PORT': db_data['DB_PORT'],
    }
}

# Loggers

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} - {levelname:4s} - {module} - {funcName} - {message}',
            'datefmt': '%d.%m.%y-%H-%M-%S',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] - {message}',
            'encoding': 'utf-8',
            'style': '{'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': './logs/debug.log',
            'mode': 'w',
            'encoding': 'utf-8',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
        },
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': False,
        },
        'plan_ilan.apps.web_site.management.commands.populate_database': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        }

    },
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
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

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

AWS_S3_OBJECT_PARAMETERS = {
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'CacheControl': 'max-age=94608000',
}

AWS_STORAGE_BUCKET_NAME = 'plan-ilan-static-server'
AWS_S3_REGION_NAME = 'eu-central-1'
AWS_ACCESS_KEY_ID = 'AKIASRQNZ5CYMZUCPQUR'
AWS_SECRET_ACCESS_KEY = '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'

# Tell django-storages the domain to use to refer to static files.
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'plan_ilan.custom_storages.StaticStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'www', 'static')
STATIC_URL = '/staticfiles/'

# SMTP Configurations
mail_data = dict(os.environ)
mail_data_file_name = 'tmp/mail_data.json'
if os.path.exists(mail_data_file_name):
    with open(mail_data_file_name, 'r') as json_file:
        mail_data = json.load(json_file)

EMAIL_BACKEND = mail_data['EMAIL_BACKEND']
EMAIL_HOST = mail_data['EMAIL_HOST']
EMAIL_PORT = mail_data['EMAIL_PORT']
EMAIL_USE_TLS = (True if mail_data['EMAIL_USE_TLS'] == "True" else False)
EMAIL_HOST_USER = mail_data['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = mail_data['EMAIL_HOST_PASSWORD']

# MEDIA Configurations
MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'plan_ilan.custom_storages.MediaStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'www', 'media')
MEDIA_URL = '/media/'

# used by debug-toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

# used by REST-framework API
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'



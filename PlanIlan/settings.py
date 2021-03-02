"""
Django settings for PlanIlan project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import json
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0p!a&2d!ui+clgkdpgj7umd+0$k)m+#@dqacj7)=r)tqyy@_#t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

INSTALLED_APPS = [
    'PlanIlan',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'PlanIlan.urls'

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

WSGI_APPLICATION = 'PlanIlan.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

db_data = dict(os.environ)
db_data_file_name = 'db_data.json'
if os.path.exists(db_data_file_name):
    with open(db_data_file_name, 'r') as json_file:
        db_data = json.load(json_file)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
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
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
        },
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': False,
        },
        'PlanIlan.management.commands.populate_database': {
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

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

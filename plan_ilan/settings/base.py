from abc import abstractmethod

from django.utils.translation import gettext_noop, gettext_lazy

from .settings import Settings
import json
import os
import socket
import sys
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from .config import config


class BaseSettings(Settings):
    """Plan Ilan project base settings"""
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    SITE_ROOT = Path(__file__).resolve().parent.parent.parent

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = '0p!a&2d!ui+clgkdpgj7umd+0$k)m+#@dqacj7)=r)tqyy@_#t'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1']

    # Application definition

    TEMPLATE_ROOT = os.path.join(SITE_ROOT, "templates")

    ROOT_URLCONF = 'plan_ilan.urls'

    @property
    def INSTALLED_APPS(self):
        apps = [
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
            'django_user_agents',
        ]
        return apps


    MIDDLEWARE = (
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django_user_agents.middleware.UserAgentMiddleware',
    )

    @property
    def TEMPLATES(self):
        return [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [self.TEMPLATE_ROOT],
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

    @property
    def DATABASES(self):
        pass

    VERBOSE_LOG_FORMAT = '{asctime}-[{levelname:4s}]-[in {filename} at {funcName}/{lineno:d}]: {message}'
    LOG_DATE_FORMAT = '%d.%m.%y-%H:%M:%S'
    SIMPLE_LOG_FORMAT = '[{levelname}]: {message}'
    THREADS_LOG_FORMAT = '[Thread:{thread:d}]-{asctime}-[{levelname:4s}]-[in {filename} at {funcName}/{lineno:d}]: {message}'

    LOGS_ROOT = os.path.join(SITE_ROOT, 'logs')

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': VERBOSE_LOG_FORMAT,
                'datefmt': LOG_DATE_FORMAT,
                'style': '{',
            },
            'simple': {
                'format': SIMPLE_LOG_FORMAT,
                'encoding': 'utf-8',
                'style': '{'
            },
            'threads': {
                'format': THREADS_LOG_FORMAT,
                'datefmt': LOG_DATE_FORMAT,
                'style': '{',
            },
        },
        'handlers': {
            'debug': {
                'level': 'DEBUG',
                'class': 'plan_ilan.logging.costume_handlers.CostumeSuffixTimedRotatingFileHandler',
                'filename': os.path.join(LOGS_ROOT, 'debug.log'),
                'when': 'D',
                'interval': 1,
                'encoding': 'utf-8',
                'formatter': 'verbose',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'simple',
            },
            'populate_database': {
                'level': 'DEBUG',
                'class': 'plan_ilan.logging.costume_handlers.CostumeSuffixTimedRotatingFileHandler',
                'filename': os.path.join(LOGS_ROOT, 'populate_database.log'),
                'when': 'D',
                'interval': 1,
                'encoding': 'utf-8',
                'formatter': 'threads',
            },
            'null': {
                'class': 'logging.NullHandler',
            }
        },
        'loggers': {
            '': {
                # root logging
                'handlers': ['debug', 'console'],
                # Always send from the root, handlers can filter levels
                'level': 'INFO',
            },
            'plan_ilan': {
                'handlers': ['debug', 'console'],
                'level': 'DEBUG',
                # Don't double log at the root logging for these.
                'propagate': False,
            },
            'plan_ilan.apps.web_site.management.commands.populate_database': {
                'handlers': ['populate_database', 'console'],
                'level': 'DEBUG',
                # Don't double log at the root logging for these.
                'propagate': False,
            },
            'django.security.DisallowedHost': {
                'handlers': ['null'],
                'propagate': False,
            },
        },
    }

    # Password validation
    # https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

    AUTH_PASSWORD_VALIDATORS = []

    # Internationalization
    # https://docs.djangoproject.com/en/3.1/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    LANGUAGES = (
        ('he', _('Hebrew')),
        ('en', _('English')),
    )

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/3.1/howto/static-files/
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(SITE_ROOT, 'static'),
        os.path.join(SITE_ROOT, 'media')
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT', cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=False)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

    # MEDIA Configurations
    MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
    MEDIA_URL = '/media/'

    @property
    def INTERNAL_IPS(self):
        return []

    # used by REST-framework API
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 25,
    }

    CRISPY_TEMPLATE_PACK = 'bootstrap4'

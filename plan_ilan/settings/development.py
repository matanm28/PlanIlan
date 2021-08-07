from plan_ilan.settings.base import BaseSettings
from .config import config


class DevelopmentSettings(BaseSettings):
    DATABASE_PREFIX = 'AWS'
    DEBUG=True

    @property
    def DATABASES(self):
        return {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'CONN_MAX_AGE': 3600,
                'NAME': config(f'{self.DATABASE_PREFIX}_DB_NAME'),
                'USER': config(f'{self.DATABASE_PREFIX}_DB_USER_NAME'),
                'PASSWORD': config(f'{self.DATABASE_PREFIX}_DB_USER_PASSWORD'),
                'HOST': config(f'{self.DATABASE_PREFIX}_DB_HOST_NAME'),
                'PORT': config(f'{self.DATABASE_PREFIX}_DB_PORT', cast=int),
            }
        }

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    # Disable password validators on development
    AUTH_PASSWORD_VALIDATORS = []

    @property
    def LOGGING(self):
        logging = super().LOGGING
        logging['handlers']['console']['level'] = 'DEBUG'
        logging['formatters']['simple']['format'] = f'{{asctime}}-[at {{pathname}} in {{funcName}}/{{lineno:d}}]-{self.SIMPLE_LOG_FORMAT}'
        # Allow other tools to create loggers
        logging['disable_existing_loggers'] = False
        return logging

    @property
    def INSTALLED_APPS(self):
        apps = super().INSTALLED_APPS
        apps.append('debug_toolbar')
        return apps

    @property
    def MIDDLEWARE(self):
        middlewares = list(super().MIDDLEWARE)
        middlewares.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        return middlewares

    @property
    def INTERNAL_IPS(self):
        return ['*']


DevelopmentSettings.load_settings(__name__)

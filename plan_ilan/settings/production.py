from .base import BaseSettings
from .config import config


class ProductionSettings(BaseSettings):
    DEBUG = False

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

    ALLOWED_HOSTS = ['plan-ilan-env.eba-aq8y523e.eu-central-1.elasticbeanstalk.com',
                     'planilan-prod.eu-central-1.elasticbeanstalk.com', ' 3.69.136.247',
                     '127.0.0.1', '52.58.94.40', '172.22.32.1', '172.31.24.250']

    @property
    def INSTALLED_APPS(self):
        apps = super().INSTALLED_APPS
        apps.append('storages')
        return apps

    DATABASE_PREFIX = 'AWS'

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

    AWS_S3_OBJECT_PARAMETERS = {
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'CacheControl': 'max-age=94608000',
    }

    AWS_ACCESS_KEY_ID = 'AKIASRQNZ5CYMZUCPQUR'
    AWS_SECRET_ACCESS_KEY = '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'

    AWS_STORAGE_BUCKET_NAME = 'plan-ilan-static-server'
    AWS_S3_REGION_NAME = 'eu-central-1'

    # Tell django-storages the domain to use to refer to static files.
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    STATICFILES_LOCATION = 'static'
    STATICFILES_STORAGE = 'plan_ilan.custom_storages.StaticStorage'
    STATIC_URL = '/staticfiles/'

    MEDIAFILES_LOCATION = 'media'
    DEFAULT_FILE_STORAGE = 'plan_ilan.custom_storages.MediaStorage'


ProductionSettings.load_settings(__name__)

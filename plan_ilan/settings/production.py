from .base import BaseSettings


class ProductionSettings(BaseSettings):
    DEBUG = False


ProductionSettings.load_settings(__name__)

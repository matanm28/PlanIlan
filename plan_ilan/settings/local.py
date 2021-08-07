from plan_ilan.settings.development import DevelopmentSettings


class LocalSettings(DevelopmentSettings):
    DATABASE_PREFIX = 'LOCAL'


LocalSettings.load_settings(__name__)

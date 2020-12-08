from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def create(cls, *args) -> 'BaseModel':
        pass

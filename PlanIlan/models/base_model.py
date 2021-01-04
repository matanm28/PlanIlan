import logging
from typing import Iterable

from django.db import models

from PlanIlan.exceptaions import CantCreateModelError


class BaseModel(models.Model):
    CANT_CREATE_MODEL_MSG = 'Parameter {} must be of type {}. Got type: {}'

    class Meta:
        abstract = True

    @classmethod
    def create_without_save(cls, *args, **kwargs) -> 'BaseModel':
        pass

    @classmethod
    def create(cls, *args, **kwargs) -> 'BaseModel':
        model = cls.create_without_save(*args, **kwargs)
        model.save()
        return model

    @classmethod
    def generate_cant_create_model_err(cls, model_type: str, param_name: str, allowed_types: Iterable[str],
                                       actual_type: str) -> CantCreateModelError:
        return CantCreateModelError(model_type, cls.CANT_CREATE_MODEL_MSG.format(param_name, ' or '.join(allowed_types),
                                                                                 actual_type))

    @classmethod
    def log_created(cls, type_name: str, id_str: str, created: bool):
        if not created:
            return
        logging.info(f'{type_name} instance created with id: {id_str}')

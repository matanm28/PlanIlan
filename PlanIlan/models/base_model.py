import logging
from typing import Iterable

from django.db import models

from PlanIlan.exceptaions import CantCreateModelError


class BaseModel(models.Model):
    WRONG_PARAMS_MSG = 'Parameter {} must be of type {}. Got type: {}'
    INVALID_PARAMS_MSG = 'Parameter {} is invalid. {}'

    class Meta:
        abstract = True

    @classmethod
    def create(cls, *args, **kwargs) -> 'BaseModel':
        pass

    @classmethod
    def generate_cant_create_model_err(cls, model_type: str, param_name: str, allowed_types: Iterable[str],
                                       actual_type: str) -> CantCreateModelError:
        return CantCreateModelError(model_type, cls.WRONG_PARAMS_MSG.format(param_name, ' or '.join(allowed_types),
                                                                            actual_type))

    @classmethod
    def generate_cant_create_model_err(cls, model_type: str, param_name: str, message: str):
        return CantCreateModelError(model_type, cls.INVALID_PARAMS_MSG.format(param_name, message))

    @classmethod
    def log_created(cls, type_name: str, id_str: str, created: bool):
        if not created:
            return
        logging.info(f'{type_name} instance created with id: {id_str}')

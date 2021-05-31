import logging
from typing import Iterable

from django.db import models

from plan_ilan.exceptaions import CantCreateModelError


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

    # todo: change to send less args
    @classmethod
    def log_created(cls, obj: 'BaseModel', created: bool):
        if not created:
            return
        logging.info(f'{type(obj).__name__} instance created with id: {obj.pk}')

    @classmethod
    def log_error(cls, err, is_exception=True):
        if is_exception:
            logging.exception(err)
        else:
            logging.error(err)

    def __repr__(self):
        fields = self._meta.fields
        fields_str = []
        for field in fields:
            fields_str.append(f'{field.attname}: {getattr(self, field.attname)}')
        return ', '.join(fields_str)

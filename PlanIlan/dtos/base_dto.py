from dataclasses import dataclass
from typing import ClassVar, Dict

from mapper.object_mapper import ObjectMapper

from PlanIlan.models import BaseModel


@dataclass
class BaseDto:
    _mapper: ClassVar[ObjectMapper] = ObjectMapper()
    _mapping_options: ClassVar[Dict]

    @classmethod
    def init_mapper(cls):
        if len(cls._mapper.mappings) == 0:
            #cls._mapper.create_map(cls.maps_from(), cls.maps_to(), mapping=cls.mapping_options())
            cls._mapping_options = cls.mapping_options()

    @classmethod
    def map(cls, model) -> 'BaseDto':
        map_to = cls.maps_to()
        obj = map_to()
        for field in map_to.__annotations__.keys():
            obj.__setattr__(field, cls.mapping_options()[
                field](model) if field in cls._mapping_options else model.__getattribute__(field))
        return obj

    @classmethod
    def mapping_options(cls):
        pass

    @classmethod
    def maps_from(cls) -> type:
        pass

    @classmethod
    def maps_to(cls) -> type:
        pass

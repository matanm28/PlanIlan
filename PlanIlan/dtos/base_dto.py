from dataclasses import dataclass
from typing import ClassVar

from mapper.object_mapper import ObjectMapper



@dataclass
class BaseDto:
    _mapper: ClassVar[ObjectMapper] = ObjectMapper()

    @classmethod
    def init_mapper(cls):
        if len(cls._mapper.mappings) == 0:
            cls._mapper.create_map(cls.maps_from(), cls.maps_to(), mapping=cls.mapping_options())

    @classmethod
    def map(cls, model) -> 'BaseDto':
        return cls._mapper.map(model, cls, allow_unmapped=True)

    @classmethod
    def mapping_options(cls):
        pass

    @classmethod
    def maps_from(cls):
        pass

    @classmethod
    def maps_to(cls):
        pass

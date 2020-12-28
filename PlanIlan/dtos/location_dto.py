from dataclasses import field

from PlanIlan.dtos.base_dto import BaseDto
from PlanIlan.models import Location


class LocationDto(BaseDto):
    building_name: str
    building_number: int = field(init=False, default=None)
    class_number: int = field(init=False, default=None)
    online: bool = field(init=False, default=False)

    @classmethod
    def mapping_options(cls):
        return {}

    @classmethod
    def maps_from(cls):
        return Location

    @classmethod
    def maps_to(cls):
        return cls



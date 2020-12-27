from dataclasses import dataclass

from PlanIlan.dtos.base_dto import BaseDto
from PlanIlan.models import Rating


class RatingDto(BaseDto):
    average: float
    amount_of_raters: int

    @classmethod
    def mapping_options(cls):
        return {}

    @classmethod
    def maps_from(cls):
        return type(Rating)

    @classmethod
    def maps_to(cls):
        return type(cls)



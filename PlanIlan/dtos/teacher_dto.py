from dataclasses import dataclass, field

from PlanIlan.dtos.base_dto import BaseDto
from PlanIlan.dtos.rating_dto import RatingDto
from PlanIlan.models import Teacher


@dataclass
class TeacherDto(BaseDto):
    title: str = field(init=False)
    name: str = field(init=False)
    rating: RatingDto = field(default=None, init=False, compare=False)

    @classmethod
    def mapping_options(cls):
        return {
            'title': lambda teacher: teacher.title.label,
            'rating': lambda teacher: RatingDto.map(teacher.teacherrating_set)
        }

    @classmethod
    def maps_from(cls):
        return Teacher

    @classmethod
    def maps_to(cls):
        return cls

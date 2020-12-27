from dataclasses import dataclass, field

from PlanIlan.dtos.base_dto import BaseDto
from PlanIlan.dtos.rating_dto import RatingDto
from PlanIlan.models import Teacher


@dataclass
class TeacherDto(BaseDto):
    title: str
    name: str
    rating: RatingDto = field(default=None, init=False, compare=False)

    @classmethod
    def mapping_options(cls):
        return {
            'title': lambda teacher: teacher.title.label,
            'rating': lambda teacher: RatingDto.map(teacher.rating)
        }

    @classmethod
    def maps_from(cls):
        t = Teacher(name='navu',title='sss')
        return type(t)

    @classmethod
    def maps_to(cls):
        return cls

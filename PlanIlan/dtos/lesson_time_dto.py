from datetime import time

from PlanIlan.dtos.base_dto import BaseDto
from PlanIlan.models import LessonTime


class LessonTimeDto(BaseDto):
    day: int
    start_time: time
    end_time: time

    @classmethod
    def mapping_options(cls):
        return {
            'day': lambda lesson_time: lesson_time.day.value
        }

    @classmethod
    def maps_from(cls):
        return type(LessonTime)

    @classmethod
    def maps_to(cls):
        return type(cls)



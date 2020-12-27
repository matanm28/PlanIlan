import sys
import logging
from datetime import datetime, time, timedelta
from django.db import models
from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import Day, BaseModel


class LessonTime(BaseModel):
    day = models.IntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @classmethod
    def create(cls, day: str, start_time: time, end_time: time) -> 'LessonTime':
        try:
            day_enum = Day.from_string(day)
            lesson_time = LessonTime(day=day_enum, start_time=start_time, end_time=end_time)
            return lesson_time
        except EnumNotExistError as err:
            logging.error(f'Error while fetching {err.enum_type} instance with {err.value}')
            logging.error(f'{err}')

    @property
    def time_delta(self) -> timedelta:
        return datetime(self.end_time) - datetime(self.start_time)

    @property
    def duration(self) -> float:
        return self.time_delta.total_seconds() / 3600

import sys
from datetime import datetime

from django.db import models

from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import Day, BaseModel


class LessonTime(BaseModel):
    day = models.IntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @classmethod
    def create(cls, day: str, start_time: datetime, end_time: datetime) -> 'LessonTime':
        try:
            day_enum = Day.get_enum(day)
            lesson_time = LessonTime(day=day_enum, start_time=start_time, end_time=end_time)
            return lesson_time
        except EnumNotExistError as err:
            print(err, file=sys.stderr)

    @property
    def duration(self):
        return datetime(self.end_time) - datetime(self.start_time)

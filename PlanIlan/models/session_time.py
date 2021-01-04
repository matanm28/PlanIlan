import sys
import logging
from datetime import datetime, time, timedelta
from typing import Any, Union

from django.db import models
from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import Day, BaseModel, Semester


class SessionTime(BaseModel):
    day = models.IntegerField(choices=Day.choices)
    semester = models.IntegerField(choices=Semester.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @classmethod
    def create_without_save(cls, semester: Union[Semester, str, int], day: Union[Day, str, int], start_time: time,
                            end_time: time) -> 'SessionTime':
        try:
            if not isinstance(semester, (Semester, str, int)):
                raise cls.generate_cant_create_model_err(cls.__name__, semester.__name__, (Semester, str, int),
                                                         type(semester))
            if isinstance(semester, str):
                semester_enum = Semester.from_string(semester)
            elif isinstance(semester, int):
                semester_enum = Semester.from_int(semester)
            else:
                semester_enum = semester

            if not isinstance(day, (Day, str, int)):
                raise cls.generate_cant_create_model_err(cls.__name__, day.__name__, (Day, str, int),
                                                         type(day))
            if isinstance(day, str):
                day_enum = Day.from_string(day)
            elif isinstance(semester, int):
                day_enum = Day.from_int(day)
            else:
                day_enum = day
            lesson_time, created = SessionTime.objects.get_or_create(day=day_enum, start_time=start_time,
                                                                     end_time=end_time, semester=semester_enum)
            cls.log_created(cls.__name__, lesson_time.id, created)
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

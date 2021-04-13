import sys
import logging
from datetime import datetime, time, timedelta
from typing import Union

from django.db import models
from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import DayEnum, BaseModel, SemesterEnum
from PlanIlan.utils.general import is_number
from PlanIlan.utils.time import Time, TimeDelta


class SessionTime(BaseModel):
    _day = models.IntegerField(choices=DayEnum.choices, db_column='day')
    _semester = models.IntegerField(choices=SemesterEnum.choices, db_column='semester')
    start_time = models.TimeField()
    end_time = models.TimeField()
    year = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['_day', '_semester', 'start_time', 'end_time', 'year']

    @classmethod
    def create(cls, semester: Union[SemesterEnum, str, int], day: Union[DayEnum, str, int], start_time: time,
               end_time: time, year: int) -> 'SessionTime':
        try:
            if not isinstance(semester, (SemesterEnum, str, int)):
                raise cls.generate_cant_create_model_err(cls.__name__, semester.__name__, (SemesterEnum, str, int),
                                                         type(semester))
            if isinstance(semester, str):
                semester_enum = SemesterEnum.from_string(semester)
            elif isinstance(semester, int):
                semester_enum = SemesterEnum.from_int(semester)
            else:
                semester_enum = semester

            if not isinstance(day, (DayEnum, str, int)):
                raise cls.generate_cant_create_model_err(cls.__name__, day.__name__, (DayEnum, str, int),
                                                         type(day))
            if isinstance(day, str):
                day_char = day
                if len(day) > 1:
                    day_char = day[0]
                day_enum = DayEnum.from_string(day_char)
            elif isinstance(semester, int):
                day_enum = DayEnum.from_int(day)
            else:
                day_enum = day
            lesson_time, created = SessionTime.objects.get_or_create(_day=day_enum, start_time=start_time,
                                                                     end_time=end_time, _semester=semester_enum,
                                                                     year=year)
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
        """
        :return:The duration of the session in hours.
        """
        return self.time_delta.total_seconds() / 3600

    @classmethod
    def format_time_to_string(cls, d: datetime) -> str:
        return d.strftime('%H:%M')

    @property
    def start_str(self) -> datetime:
        return self.format_time_to_string(self.start_time)

    @property
    def end_str(self) -> datetime:
        return self.format_time_to_string(self.end_time)

    def get_hours_list(self, jump: int = 1, jump_by: str = 'hours'):
        jump_by_multiplier = {'hours': 3600, 'minutes': 60, 'seconds': 1}
        if not jump_by.lower() in jump_by_multiplier:
            jump_by = 'hours'
        if not isinstance(jump, int):
            if is_number(jump):
                jump = int(float(jump))
            else:
                jump = 1
        current_time = Time(self.start_time.hour, self.start_time.minute, self.start_time.second)
        end_time = Time(self.end_time.hour, self.end_time.minute, self.end_time.second)
        times_list = []
        time_delta = TimeDelta(seconds=jump_by_multiplier[jump_by] * jump)
        while current_time < end_time:
            times_list.append(current_time)
            current_time += time_delta
        return times_list

    @property
    def day(self):
        return DayEnum.from_int(self._day)

    @property
    def semester(self):
        return SemesterEnum.from_int(self._semester)

    def __repr__(self):
        return f'semester: {self.semester.label}, day: {self.day}, time: {self.start_str}-{self.end_str}'

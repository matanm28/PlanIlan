from datetime import datetime, time, timedelta
from threading import Lock

from django.db import models

from plan_ilan.utils.decorators import static_vars
from . import BaseModel, Day, Semester
from plan_ilan.utils.general import is_number
from plan_ilan.utils.time import Time, TimeDelta


class LessonTime(BaseModel):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='lesson_times')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='lesson_times')
    start_time = models.TimeField()
    end_time = models.TimeField()
    year = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['day', 'start_time', 'end_time']
        unique_together = ['day', 'semester', 'start_time', 'end_time', 'year']
        db_table = 'lesson_times'

    @classmethod
    def create(cls, semester: Semester, day: Day, start_time: time,
               end_time: time, year: int) -> 'LessonTime':
        lesson_time, created = LessonTime.objects.get_or_create(day=day, start_time=start_time,
                                                                end_time=end_time, semester=semester,
                                                                year=year)
        cls.log_created(lesson_time, created)
        return lesson_time

    @classmethod
    @static_vars(mutex=Lock())
    def create_thread_safe(cls, semester: Semester, day: Day, start_time: time,
                           end_time: time, year: int) -> 'LessonTime':
        try:
            cls.create_thread_safe.mutex.acquire()
            return cls.create(semester, day, start_time, end_time, year)
        finally:
            cls.create_thread_safe.mutex.release()

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

    def time_str(self, delim='-'):
        return f'{self.start_str}{delim}{self.end_str}'

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

    def __repr__(self):
        return f'semester: {self.semester.label}, day: {self.day}, time: {self.start_str}-{self.end_str}'

    def __str__(self) -> str:
        return f'יום {self.day.full_label}, {self.time_str()} ({self.semester.label})'

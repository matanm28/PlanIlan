from typing import List, Tuple
import datetime
from django.db import models

from plan_ilan.apps.web_site.models import BaseModel, Day


class Interval(BaseModel):
    left = models.FloatField(default=float('-inf'))
    right = models.FloatField(default=float('inf'))

    @classmethod
    def create(cls, left: float, right: float) -> 'Interval':
        if left > right:
            left, right = right, left
        interval, created = cls.objects.get_or_create(left=round(left, 1), right=round(right, 1))
        cls.log_created(interval, created)
        return Interval

    @property
    def size(self) -> float:
        return self.right - self.left

    def get_overlap(self, other: 'Interval') -> float:
        return max(0, min(self.right, other.right) - max(self.left, other.left))

    def is_overlapping(self, other: 'Interval') -> bool:
        return self.get_overlap(other) > 0

    class Meta:
        ordering = ['pk']
        db_table = 'intervals'


class Time(BaseModel):
    start = models.TimeField()
    end = models.TimeField()

    @classmethod
    def create(cls, start: datetime.time, end: datetime.time) -> 'Time':
        if start > end:
            start, end = end, start
        time, created = Time.objects.get_or_create(start=start, end=end)
        cls.log_created(time, created)
        return time

    def is_overlapping(self, other: 'Time') -> bool:
        if self.start <= other.start:
            earlier, later = self, other
        else:
            earlier, later = other, self
        return later.start <= earlier.end

    class Meta:
        ordering = ['start', 'end']
        db_table = 'times'


class BlockedTimePeriod(BaseModel):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='blocked_times')
    blocked_time_periods = models.ManyToManyField(Time, related_name='blocked_time_periods')

    @classmethod
    def create(cls, day: Day, timetable: Timetable,
               blocked_times: List[Tuple[datetime.time, datetime.time]]) -> 'BlockedTimePeriod':
        blocked_time_period, created = cls.objects.get_or_create(day=day, timetable=timetable)
        cls.log_created(blocked_time_period, created)
        if created:
            blocked_time_period.times.set(blocked_times)
        else:
            # todo: what's the wanted behavior?
            blocked_time_period.times.add(blocked_times)
        return blocked_time_period

    class Meta:
        ordering = ['timetable', 'day']
        db_table = 'blocked_time_period'

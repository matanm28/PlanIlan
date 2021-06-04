from datetime import datetime

from django.db import models

from plan_ilan.apps.web_site.models import BaseModel
from plan_ilan import costume_fields


class TimeInterval(BaseModel):
    start = costume_fields.ImprovedTimeField()
    end = costume_fields.ImprovedTimeField()

    @classmethod
    def create(cls, start: datetime.time, end: datetime.time) -> 'TimeInterval':
        if start > end:
            start, end = end, start
        time_interval, created = TimeInterval.objects.get_or_create(start=start, end=end)
        cls.log_created(time_interval, created)
        return time_interval

    def is_overlapping(self, other: 'TimeInterval') -> bool:
        return self.get_overlap(other) > 0
        # if self.start <= other.start:
        #     earlier, later = self, other
        # else:
        #     earlier, later = other, self
        # return later.start <= earlier.end

    def get_overlap(self, other: 'TimeInterval') -> float:
        return max(0, min(self.end, other.end) - max(self.start, other.start))

    class Meta:
        ordering = ['start', 'end']
        db_table = 'time_intervals'


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

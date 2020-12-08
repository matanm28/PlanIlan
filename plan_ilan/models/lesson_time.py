from datetime import datetime

from django.db import models

from plan_ilan.models import Day


class LessonTime(models.Model):
    day = models.IntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @property
    def duration(self):
        return datetime(self.end_time) - datetime(self.start_time)

    @classmethod
    def create(cls, day: str, start_time: datetime, end_time: datetime):
        day_enum = Day.get_enum(day)
        day = LessonTime(day=day_enum, start_time=start_time, end_time=end_time)
        day.save()

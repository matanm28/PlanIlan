from django.db import models
from datetime import datetime

from plan_ilan.models import Day


class LessonTime(models.Model):
    day = models.IntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @property
    def duration(self):
        return datetime(self.end_time) - datetime(self.start_time)

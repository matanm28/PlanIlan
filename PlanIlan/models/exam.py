from datetime import datetime

from django.db import models

from PlanIlan.models import BaseModel, ExamPeriod


class Exam(BaseModel):
    period = models.ForeignKey(ExamPeriod, on_delete=models.CASCADE)
    date = models.DateTimeField()

    class Meta:
        unique_together = ['period', 'date']

    @classmethod
    def create(cls, period: ExamPeriod, date: datetime) -> 'Exam':
        exam, created = Exam.objects.get_or_create(period=period, date=date)
        cls.log_created(cls.__name__, exam.id, created)
        return exam

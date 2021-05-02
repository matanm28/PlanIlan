from datetime import datetime

from django.db import models

from PlanIlan.models import BaseModel, ExamPeriod


class Exam(BaseModel):
    period = models.ForeignKey(ExamPeriod, on_delete=models.CASCADE, related_name='exams')
    date = models.DateTimeField()

    class Meta:
        unique_together = ['period', 'date']

    @classmethod
    def create(cls, period: ExamPeriod, date: datetime) -> 'Exam':
        exam, created = Exam.objects.get_or_create(period=period, date=date)
        cls.log_created(exam, created)
        return exam

    def __str__(self) -> str:
        return f'{self.date.strftime("%d.%m.%y, %H:%M")} ({self.period.label})'

from datetime import datetime
from typing import Any, Union

from django.db import models

from PlanIlan.models import BaseModel, ExamPeriod, Course


class Exam(BaseModel):
    period = models.IntegerField(choices=ExamPeriod.choices)
    date = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name='exams')

    @classmethod
    def create(cls, period: Union[ExamPeriod, str, int], date: datetime, course: 'Course') -> 'Exam':
        if not isinstance(period, (ExamPeriod, str, int)):
            raise cls.generate_cant_create_model_err(cls.__name__, period.__name__, (ExamPeriod.__name__, str, int),
                                                     type(period))
        if isinstance(period, str):
            period = ExamPeriod.from_string(period)
        elif isinstance(period, int):
            period = ExamPeriod.from_int(period)
        exam, created = Exam.objects.get_or_create(period=period, date=date, course=course)
        cls.log_created(cls.__name__, exam.id, created)
        return exam

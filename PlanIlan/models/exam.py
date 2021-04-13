from datetime import datetime
from typing import Any, Union

from django.db import models

from PlanIlan.models import BaseModel, ExamPeriodEnum, Course
from PlanIlan.utils.general import name_of


class Exam(BaseModel):
    period = models.IntegerField(choices=ExamPeriodEnum.choices)
    date = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name='exams')

    class Meta:
        unique_together = ['period','date']

    @classmethod
    def create(cls, period: Union[ExamPeriodEnum, str, int], date: datetime, course: Course) -> 'Exam':
        if not isinstance(period, (ExamPeriodEnum, str, int)):
            raise cls.generate_cant_create_model_err(cls.__name__, period.__name__, (name_of(ExamPeriodEnum), str, int),
                                                     type(period))
        if isinstance(period, str):
            period = ExamPeriodEnum.from_string(period)
        elif isinstance(period, int):
            period = ExamPeriodEnum.from_int(period)
        exam, created = Exam.objects.get_or_create(period=period, date=date, course=course)
        cls.log_created(cls.__name__, exam.id, created)
        return exam

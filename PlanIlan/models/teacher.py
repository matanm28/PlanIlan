from django.db import models

from PlanIlan.models import TeacherTitle, BaseModel


class Teacher(BaseModel):
    name = models.CharField(primary_key=True, max_length=80)
    title = models.IntegerField(choices=TeacherTitle.choices)

    @classmethod
    def create(cls, name: str, title: str) -> 'Teacher':
        title_enum = TeacherTitle.get_enum(title)
        teacher = Teacher(name=name, title=title_enum)
        return teacher

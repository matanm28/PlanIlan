from typing import Any

from django.db import models

from PlanIlan.exceptaions import CantCreateModelError
from PlanIlan.models import TeacherTitle, BaseModel, Rating


class Teacher(BaseModel):
    name = models.CharField(max_length=80)
    title = models.IntegerField(choices=TeacherTitle.choices)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE, null=True, related_name='of_teacher')

    @classmethod
    def create(cls, name: str, title: Any) -> 'Teacher':
        if not isinstance(title, (TeacherTitle, str, int)):
            raise CantCreateModelError(Teacher.__name__,
                                       cls.generate_cant_create_model_err((Teacher.__name__, str, int), type(title)))
        if isinstance(title, str):
            title_enum = TeacherTitle.from_string(title)
        elif isinstance(title, int):
            title_enum = TeacherTitle.from_int(title)
        else:
            title_enum = title
        teacher, created = Teacher.objects.get_or_create(name=name, title=title_enum,
                                                         defaults={'rating': Rating.create})
        cls.log_created(cls.__name__, teacher.id, created)
        return teacher

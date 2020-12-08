from django.db import models

from plan_ilan.models import TeacherTitle


class Teacher(models.Model):
    name = models.CharField(primary_key=True, max_length=80)
    title = models.IntegerField(choices=TeacherTitle.choices)

    @classmethod
    def create(cls, name: str, title: str):
        title_enum = TeacherTitle.get_enum(title)
        teacher = Teacher(name=name, title=title_enum)
        teacher.save()

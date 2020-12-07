from django.db import models

from plan_ilan.models import TeacherTitle


class Teacher(models.Model):
    name = models.CharField(primary_key=True, max_length=80)
    title = models.IntegerField(choices=TeacherTitle.choices)

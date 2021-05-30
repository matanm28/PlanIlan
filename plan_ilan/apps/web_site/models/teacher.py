from typing import List

from django.db import models

from . import BaseModel
import plan_ilan.apps.web_site.models as my_models
from .enums import Title, Faculty, Department
from ..storage import OverwriteStorage
from django.db.models import Avg, QuerySet


def user_directory_path(instance: 'Teacher', filename: str):
    # file will be uploaded to MEDIA_ROOT/teachers/<name>/profile_pic.<extension>
    return fr'teachers\{instance.name}\profile.{filename.split(".")[-1]}'


overwrite_storage = OverwriteStorage()


class Teacher(BaseModel):
    name = models.CharField(max_length=80)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='teachers')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='teachers')
    phone = models.CharField(max_length=12, null=True)
    email = models.EmailField(null=True)
    office = models.CharField(max_length=100, null=True)
    website_url = models.URLField(null=True)
    image = models.ImageField(upload_to=user_directory_path, storage=overwrite_storage, null=True)

    class Meta:
        ordering = ['name', 'title', 'pk']
        unique_together = ['name', 'title']
        db_table = 'teachers'

    @classmethod
    def create(cls, name: str, title: Title, faculty: Faculty) -> 'Teacher':
        teacher, created = Teacher.objects.get_or_create(name=name, title=title, faculty=faculty,
                                                         defaults={
                                                             'phone': None,
                                                             'email': None,
                                                             'office': None,
                                                             'website_url': None,
                                                             'image': None})
        cls.log_created(teacher, created)
        return teacher

    @property
    def departments(self) -> QuerySet[Department]:
        # pk is used for faster query execution
        return Department.objects.filter(courses__lessons__teachers__pk=self.pk).distinct()

    @property
    def title_and_name(self):
        return f'{self.title.label} {self.name}'.strip()

    @property
    def slug(self):
        return f'teacher-{self.pk}'

    @property
    def average_rating(self) -> float:
        return self.ratings.aggregate(average_value=Avg('value'))['average_value']

    @property
    def courses(self):
        return my_models.Course.objects.filter(lessons__teachers=self).distinct()

    def __repr__(self):
        return f'id: {self.pk} name: {self.title_and_name}'

    def __str__(self):
        return f'{self.title_and_name}'

from typing import Any, Union

from django.db import models, transaction, IntegrityError

from PlanIlan.exceptaions import CantCreateModelError
from PlanIlan.models import TitleEnum, BaseModel, Rating, Location
from PlanIlan.models.enums import FacultyEnum, Title, Faculty
from PlanIlan.storage import OverwriteStorage
from PlanIlan.utils.general import name_of


def user_directory_path(instance: 'Teacher', filename: str):
    # file will be uploaded to MEDIA_ROOT/"<title> <full_name>"/<id>/"profile_pic.<extension>"
    return fr'{instance.name}\profile.{filename.split(".")[-1]}'


overwrite_storage = OverwriteStorage()


class Teacher(BaseModel):
    name = models.CharField(max_length=80)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12, null=True)
    email = models.EmailField(null=True)
    office = models.CharField(max_length=100, null=True)
    website_url = models.URLField(null=True)
    image = models.ImageField(upload_to=user_directory_path, storage=overwrite_storage, null=True)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'title']

    def __str__(self):
        return f'{self.title_and_name}'

    @classmethod
    def create(cls, name: str, title: Title, faculty: Faculty) -> 'Teacher':
        teacher, created = Teacher.objects.get_or_create(name=name, title=title,
                                                         defaults={
                                                             'rating': Rating.create,
                                                             'faculty': faculty,
                                                             'phone': None,
                                                             'email': None,
                                                             'office': None,
                                                             'website_url': None,
                                                             'image': None})
        cls.log_created(cls.__name__, teacher.id, created)
        return teacher

    @property
    def title_and_name(self):
        return f'{self.title.label} {self.name}'.strip()

    def __repr__(self):
        return f'id: {self.id} name: {self.title_and_name}'

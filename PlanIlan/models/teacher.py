from typing import Any

from django.db import models, transaction, IntegrityError

from PlanIlan.exceptaions import CantCreateModelError
from PlanIlan.models import TeacherTitle, BaseModel, Rating, Location


def user_directory_path(instance: 'Teacher', filename: str):
    # file will be uploaded to MEDIA_ROOT/"<title> <full_name>"/<id>/"profile_pic.<extension>"
    return fr'{instance.title_and_name}\{instance.id}\profile_pic.{filename.split(".")[-1]}'


class Teacher(BaseModel):
    name = models.CharField(max_length=80)
    _title = models.IntegerField(choices=TeacherTitle.choices, db_column='title')
    email = models.EmailField(null=True)
    photo = models.ImageField(upload_to=user_directory_path, null=True)
    office_location = models.CharField(max_length=75, null=True)
    office_number = models.CharField(max_length=16, null=True)
    website_url = models.URLField(null=True)
    rating = models.OneToOneField(Rating, on_delete=models.DO_NOTHING, null=True, related_name='of_teacher')

    class Meta:
        unique_together = ['name', '_title']

    def __str__(self):
        return f'{self.title_and_name}'

    @classmethod
    def create(cls, name: str, title: Any) -> 'Teacher':
        if not isinstance(title, (TeacherTitle, str, int)):
            raise cls.generate_cant_create_model_err((Teacher.__name__, str, int), type(title))
        if isinstance(title, str):
            title_enum = TeacherTitle.from_string(title)
        elif isinstance(title, int):
            title_enum = TeacherTitle.from_int(title)
        else:
            title_enum = title
        teacher, created = Teacher.objects.get_or_create(name=name, _title=title_enum, defaults={'rating': Rating.create})
        # # thread safe get_or_create
        # # https://www.agiliq.com/blog/2013/08/writing-thread-safe-django-code/
        # created = False
        # try:
        #     teacher = Teacher.objects.get(name=name, _title=title_enum)
        # except Teacher.DoesNotExist:
        #     try:
        #         with transaction.atomic():
        #             teacher = Teacher.objects.create(name=name, _title=title_enum, rating=Rating.create())
        #         created = True
        #     except IntegrityError:
        #         teacher = Teacher.objects.get(name=name, _title=title_enum)
        cls.log_created(cls.__name__, teacher.id, created)
        return teacher

    @property
    def title_and_name(self):
        return f'{self.title.label} {self.name}'.strip()

    @property
    def title(self):
        return TeacherTitle.from_int(self._title)

    def __repr__(self):
        return f'id: {self.id} name: {self.title_and_name}'

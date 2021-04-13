from typing import Any, Union

from django.db import models, transaction, IntegrityError

from PlanIlan.exceptaions import CantCreateModelError
from PlanIlan.models import TeacherTitleEnum, BaseModel, Rating, Location
from PlanIlan.models.enums import FacultyEnum
from PlanIlan.storage import OverwriteStorage
from PlanIlan.utils.general import name_of


def user_directory_path(instance: 'Teacher', filename: str):
    # file will be uploaded to MEDIA_ROOT/"<title> <full_name>"/<id>/"profile_pic.<extension>"
    return fr'{instance.name}\profile.{filename.split(".")[-1]}'


overwrite_storage = OverwriteStorage()


class Teacher(BaseModel):
    name = models.CharField(max_length=80)
    _title = models.IntegerField(choices=TeacherTitleEnum.choices, db_column='title')
    _faculty = models.IntegerField(choices=FacultyEnum.choices, db_column='faculty', null=True)
    phone = models.CharField(max_length=12, null=True)
    email = models.EmailField(null=True)
    office = models.CharField(max_length=100, null=True)
    website_url = models.URLField(null=True)
    image = models.ImageField(upload_to=user_directory_path, storage=overwrite_storage, null=True)
    rating = models.OneToOneField(Rating, on_delete=models.DO_NOTHING, null=True, related_name='of_teacher')

    class Meta:
        unique_together = ['name', '_title']

    def __str__(self):
        return f'{self.title_and_name}'

    @classmethod
    def create(cls, name: str, title: Any) -> 'Teacher':
        if not isinstance(title, (TeacherTitleEnum, str, int)):
            raise cls.generate_cant_create_model_err((Teacher.__name__, str, int), type(title))
        if isinstance(title, str):
            title_enum = TeacherTitleEnum.from_string(title)
        elif isinstance(title, int):
            title_enum = TeacherTitleEnum.from_int(title)
        else:
            title_enum = title
        teacher, created = Teacher.objects.get_or_create(name=name, _title=title_enum, defaults={'rating': Rating.create})
        cls.log_created(cls.__name__, teacher.id, created)
        return teacher

    @property
    def title_and_name(self):
        return f'{self.title.label} {self.name}'.strip()

    @property
    def title(self):
        return TeacherTitleEnum.from_int(self._title)

    @property
    def faculty(self):
        return FacultyEnum.from_int(self._faculty)

    def __repr__(self):
        return f'id: {self.id} name: {self.title_and_name}'


class Faculty(BaseModel):
    name = models.IntegerField(choices=FacultyEnum.choices, db_column='faculty')
    teachers = models.ManyToManyField(Teacher, related_name='faculties')

    @classmethod
    def create(cls, faculty: Union[str, int, FacultyEnum]) -> 'BaseModel':
        if not isinstance(faculty, (str, int, FacultyEnum)):
            raise cls.generate_cant_create_model_err(name_of(cls), name_of(faculty), (str, int, FacultyEnum), type(faculty))
        if isinstance(faculty, str):
            faculty = FacultyEnum.from_string(faculty)
        elif isinstance(faculty, int):
            faculty = FacultyEnum.from_int(faculty)
        obj, created = Faculty.objects.get_or_create(_faculty=faculty)
        cls.log_created(name_of(cls), obj.id, created)
        return obj

    @property
    def faculty(self) -> FacultyEnum:
        return FacultyEnum.from_int(self._faculty)

import sys
import logging
import uuid
from typing import List, Union
from django.db import models

from PlanIlan.exceptaions import CantCreateModelError
from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import BaseModel, SessionTime, Location, Department, Teacher, Rating, SessionType


class Course(BaseModel):
    code = models.CharField(primary_key=True, max_length=10, editable=False)
    name = models.CharField(max_length=100)
    _department = models.IntegerField(choices=Department.choices, db_column='department')
    syllabus_link = models.URLField(null=True)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE, null=True, related_name='of_course')

    @property
    def id(self):
        return self.code

    @staticmethod
    def get_faculty_code_from_course_id(course_id: str) -> str:
        if not course_id:
            raise ValueError('Value must not be null or empty')
        index = 2
        if len(course_id) == 6:
            index = 3
        return course_id[:index]

    @classmethod
    def create(cls, code: str, name: str, department: Union[Department, str, int], syllabus_link: str = None):
        try:
            if not isinstance(department, (Department, str, int)):
                raise cls.generate_cant_create_model_err(cls.__name__, department.__name__, (Department.__name__, str),
                                                         type(department))
            if isinstance(department, str):
                department = Department.from_string(department)
            if isinstance(department, int):
                department = Department.from_int(department)
            course, created = Course.objects.get_or_create(code=code, name=name,
                                                           defaults={'syllabus_link': syllabus_link,
                                                                     '_department': department,
                                                                     'rating': Rating.create})
            cls.log_created(cls.__name__, course.id, created)
            return course
        except EnumNotExistError as err:
            raise err

    @property
    def department(self) -> Department:
        return Department.from_int(self._department)

    def get_instances(self):
        return self.course_instances.all()


class CourseInstance(BaseModel):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT, related_name='course_instances')
    group = models.CharField(max_length=3)
    _session_type = models.IntegerField(choices=SessionType.choices, db_column='session_type')
    details_link = models.URLField(null=True)
    teachers = models.ManyToManyField(Teacher, related_name='teaches_courses')
    session_times = models.ManyToManyField(SessionTime, related_name='courses')
    points = models.FloatField(null=True)
    locations = models.ManyToManyField(Location, related_name='courses')

    @classmethod
    def create(cls, code: str, group: str, name: str, teachers: List[Teacher], session_type: SessionType,
               department: Union[Department, str, int], session_times: List[SessionTime], locations: List[Location],
               points: float = None, link: str = None, syllabus_link: str = None) -> 'CourseInstance':
        if not len(teachers) > 0:
            raise cls.generate_cant_create_model_err(cls.__name__, teachers.__name__, "staff list can't be empty")
        if not len(session_times) > 0:
            raise cls.generate_cant_create_model_err(cls.__name__, session_times.__name__, "session_times list can't be empty")
        if not len(locations) > 0:
            raise cls.generate_cant_create_model_err(cls.__name__, locations.__name__, "locations list can't be empty")
        try:
            course = Course.create(code, name, department, syllabus_link)
            course_instance_id = f'{code}_{group}_{session_times[0].year}'
            course_instance, created = CourseInstance.objects.get_or_create(id=course_instance_id, course=course,
                                                                            defaults={'group': group,
                                                                                      '_session_type': session_type,
                                                                                      'details_link': link,
                                                                                      'points': points})
            course_instance.teachers.set(teachers)
            course_instance.locations.set(locations)
            course_instance.session_times.set(session_times)
            cls.log_created(cls.__name__, course_instance.id, created)
            return course_instance
        except EnumNotExistError as err:
            raise err
        except Exception as e:
            raise e

    @property
    def session_type(self) -> SessionType:
        return SessionType.from_int(self._session_type)

    @property
    def department(self) -> Department:
        return self.course.department

    def get_course_session_types(self) -> List[SessionType]:
        session_types = set()
        for course_instance in CourseInstance.objects.filter(code=self.course.code):
            session_types.add(course_instance.session_type)
        return list(session_types)

    @property
    def code_and_group(self):
        return f'{self.code}-{self.group}'

    @property
    def code(self) -> str:
        return self.course.code

    @property
    def name(self) -> str:
        return self.course.name

    def get_teacher(self, index: int = 0):
        teachers_list = self.teachers.all()
        if len(teachers_list) - 1 > index:
            # todo: make special exception
            raise Exception('teacher index is invalid')
        return teachers_list[index]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.code_and_group}: {self.name} ({self.points:.1f})'

    def get_full_string(self):
        return f'{self.code_and_group}: {self.name}, מרצה: {self.teacher.title_and_name}'

    @property
    def teacher(self):
        return self.get_teacher()

    @property
    def semester(self):
        semesters = set()
        for session_times in self.session_times.all():
            semesters.add(session_times.semester.value)
        if len(semesters) != 1:
            if len(semesters) == 0:
                logging.warning('Course with no listed semesters')
            else:
                logging.warning('Course with more than one different semesters')
        return semesters.pop()

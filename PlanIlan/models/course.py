import sys
import logging
import uuid
from typing import List, Union
from django.db import models

from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import BaseModel, SessionTime, Location, Department, Teacher, Rating, SessionType


class Course(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160)
    code = models.CharField(max_length=10)
    group = models.CharField(max_length=3)
    _department = models.IntegerField(choices=Department.choices, db_column='department')
    _session_type = models.IntegerField(choices=SessionType.choices, db_column='session_type')
    points = models.FloatField(null=True)
    details_link = models.URLField(null=True)
    syllabus_link = models.URLField(null=True)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE, null=True, related_name='of_course')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='courses')
    session_times = models.ManyToManyField(SessionTime, related_name='courses')
    locations = models.ManyToManyField(Location, related_name='courses')

    @staticmethod
    def get_faculty_code_from_course_id(course_id: str) -> str:
        if not course_id:
            raise ValueError('Value must not be null or empty')
        index = 2
        if len(course_id) == 6:
            index = 3
        return course_id[:index]

    @classmethod
    def create(cls, code: str, group: str, name: str, teacher: Teacher, session_type: SessionType,
               department: Union[Department, str], session_times: List[SessionTime],
               locations: List[Location], points: float, link: str, syllabus_link: str) -> 'Course':
        try:
            if not isinstance(department, (Department, str, int)):
                raise cls.generate_cant_create_model_err(cls.__name__, department.__name__, (Department.__name__, str),
                                                         type(department))
            if isinstance(department, str):
                department = Department.from_string(department)
            if isinstance(department, int):
                department = Department.from_int(department)
            course, created = Course.objects.get_or_create(code=code, group=group, name=name, teacher=teacher,
                                                           _department=department, _session_type=session_type,
                                                           defaults={'details_link': link, 'points': points,
                                                                     'rating': Rating.create,
                                                                     'syllabus_link': syllabus_link})
            course.locations.set(locations)
            course.session_times.set(session_times)
            cls.log_created(cls.__name__, course.id, created)
            return course
        except EnumNotExistError as err:
            raise err

    @property
    def session_type(self):
        return SessionType.from_int(self._session_type)

    @property
    def department(self):
        return Department.from_int(self._department)

    def get_course_session_types(self):
        session_types = set()
        for course in Course.objects.filter(code=self.code):
            session_types.add(course.session_type)
        return list(session_types)

    @property
    def code_and_group(self):
        return f'{self.code}-{self.group}'

    def __repr__(self):
        return f'{self.code_and_group}: {self.name}'

    def __str__(self):
        return f'{self.code_and_group}: {self.name}'

    def get_full_string(self):
        return f'{self.code_and_group}: {self.name}, מרצה: {self.teacher.title_and_name}'

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

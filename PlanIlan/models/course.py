import sys
import logging
from typing import List, Union
from django.db import models

from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import BaseModel, SessionTime, Location, Department, Teacher, Rating, Exam


class Course(BaseModel):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=160)
    department = models.IntegerField(choices=Department.choices)
    points = models.FloatField(null=True)
    details_link = models.URLField(null=True)
    syllabus_link = models.URLField(null=True)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE, null=True, related_name='of_course')
    # todo: decide what to do with multiple teachers - [27345-01,89230-01] for example
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
    def create_without_save(cls, course_id: str, name: str, teacher: Teacher, department: Union[Department, str, int],
                            session_times: List[SessionTime], locations: List[Location], exams: List[Exam],
                            points: float, link: str, syllabus_link: str) -> 'Course':
        try:
            department_enum = Department.from_int(int(cls.get_faculty_code_from_course_id(course_id)))
            course = Course(id=course_id, name=name, teacher=teacher, department=department_enum, details_link=link,
                            points=points, rating=Rating.create(), syllabus_link=syllabus_link)
            for location in locations:
                course.locations.add(location)
            for lesson_time in session_times:
                course.session_times.add(lesson_time)
            for exam in exams:
                exam.course = course
            return course
        except EnumNotExistError as err:
            raise err

    @property
    def group_code(self) -> str:
        return self.id[-2:]

    @property
    def code(self) -> str:
        return self.id[:-2]

    @property
    def faculty_code(self) -> str:
        return Course.get_faculty_code_from_course_id(self.id)

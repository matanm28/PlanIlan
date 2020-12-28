import sys
import logging
from typing import List
from django.db import models

from PlanIlan.exceptaions.cant_create_model_error import CantCreateModelError
from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import BaseModel, LessonTime, Location, Faculty, Semester, Teacher


class Course(BaseModel):
    @staticmethod
    def get_faculty_code_from_course_id(course_id: str) -> str:
        if not course_id:
            raise ValueError('Value must not be null or empty')
        index = 2
        if len(course_id) == 6:
            index = 3
        return course_id[:index]

    @classmethod
    def create(cls, course_id: str, name: str, teacher: Teacher, lesson_times: List[LessonTime],
               locations: Location,
               semester: str, link: str) -> 'Course':
        # if len(lesson_times) != len(locations):
        #     reason = f'Amount of locations ({len(locations)}) differs from the amount of lesson times ({len(lesson_times)})'
        #     raise CantCreateModelError(cls.__name__, reason)
        try:
            faculty_enum = Faculty.from_int(int(cls.get_faculty_code_from_course_id(course_id)))
            semester_enum = Semester.from_string(semester)
            course = Course(id=course_id, name=name, teacher=teacher, faculty=faculty_enum,
                            semester=semester_enum, details_link=link)
            course.locations.add(locations)
            course.lesson_times.add(lesson_times[0])

            # course.locations.add(locations)
            # for lesson_time in lesson_times:
            #     course.lesson_times.add(lesson_time)
            return course
        except EnumNotExistError as err:
            raise err

    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=80)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    lesson_times = models.ManyToManyField(LessonTime)
    locations = models.ManyToManyField(Location)
    faculty = models.IntegerField(choices=Faculty.choices)
    semester = models.IntegerField(choices=Semester.choices)
    details_link = models.URLField(null=True)

    @property
    def group_code(self) -> str:
        return self.id[-2:]

    @property
    def code(self) -> str:
        return self.id[:-2]

    @property
    def faculty_code(self) -> str:
        return Course.get_faculty_code_from_course_id(self.id)

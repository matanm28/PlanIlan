import sys
from typing import List
from django.db import models
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
               locations: List[Location],
               semester: str, link: str) -> 'Course':
        if len(lesson_times) != len(locations):
            return None
        try:
            faculty_enum = Faculty.from_int(int(cls.get_faculty_code_from_course_id(course_id)))
            semester_enum = Semester.from_string(semester)
            course = Course(course_id=course_id, name=name, teacher=teacher, lesson_times=lesson_times,
                            locations=locations, faculty=faculty_enum, semester=semester_enum, details_link=link)
            return course
        except EnumNotExistError as err:
            print(err, file=sys.stderr)
            return None

    course_id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=80)
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    lesson_times = models.ManyToManyField('LessonTime')
    locations = models.ManyToManyField('Location')
    faculty = models.IntegerField(choices=Faculty.choices)
    semester = models.IntegerField(choices=Semester.choices)
    details_link = models.URLField(null=True)

    @property
    def group_code(self) -> str:
        return self.course_id[-2:]

    @property
    def code(self) -> str:
        return self.course_id[:-2]

    @property
    def faculty_code(self) -> str:
        return Course.get_faculty_code_from_course_id(self.course_id)

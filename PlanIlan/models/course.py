import sys
import logging
import uuid
from typing import List, Union
from django.db import models

from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError
from PlanIlan.models import BaseModel, SessionTime, Location, Teacher, Rating, LessonTypeEnum, Exam
from PlanIlan.models.enums import Day, Department, Faculty, LessonType


class Course(BaseModel):
    code = models.CharField(primary_key=True, max_length=10, editable=False)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    syllabus_link = models.URLField(null=True)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE, null=True, related_name='of_course')
    exams = models.ManyToManyField(Exam)

    @staticmethod
    def get_faculty_code_from_course_id(course_id: str) -> str:
        if not course_id:
            raise ValueError('Value must not be null or empty')
        index = 2
        if len(course_id) == 6:
            index = 3
        return course_id[:index]

    @classmethod
    def create(cls, code: str, name: str, department: Department, faculty: Faculty, exams: List[Exam],
               syllabus_link: str = None):
        course, created = Course.objects.get_or_create(code=code,
                                                       defaults={
                                                           'name': name,
                                                           'syllabus_link': syllabus_link,
                                                           'department': department,
                                                           'faculty': faculty,
                                                           'rating': Rating.create})
        course.exams.set(exams)
        cls.log_created(cls.__name__, course.pk, created)
        if not created and not course.syllabus_link and syllabus_link:
            course.syllabus_link = syllabus_link
            course.save()
        return course

    def get_lessons(self):
        return self.lessons.all()


class Lesson(BaseModel):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    group = models.CharField(max_length=3)
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE)
    details_link = models.URLField(null=True)
    teachers = models.ManyToManyField(Teacher, related_name='teaches_courses')
    session_times = models.ManyToManyField(SessionTime, related_name='courses')
    points = models.FloatField(null=True)
    locations = models.ManyToManyField(Location, related_name='courses')

    @classmethod
    def create(cls, code: str, group: str, name: str, teachers: List[Teacher], session_type: LessonType,
               faculty: Faculty, department: Department, session_times: List[SessionTime], locations: List[Location],
               exams: List[Exam], points: float = None, link: str = None, syllabus_link: str = None) -> 'Lesson':
        if not len(teachers) > 0:
            raise cls.generate_cant_create_model_err(cls.__name__, teachers.__name__, "staff list can't be empty")
        if not len(session_times) > 0:
            raise cls.generate_cant_create_model_err(cls.__name__, session_times.__name__,
                                                     "session_times list can't be empty")
        if not len(locations) > 0:
            raise cls.generate_cant_create_model_err(cls.__name__, locations.__name__, "locations list can't be empty")
        try:
            course = Course.create(code, name, department, faculty, exams, syllabus_link)
            lesson_id = f'{code}_{group}_{session_times[0].year}'
            lesson, created = Lesson.objects.get_or_create(id=lesson_id,
                                                           defaults={
                                                               'course': course,
                                                               'group': group,
                                                               'lesson_type': session_type,
                                                               'details_link': link,
                                                               'points': points})
            lesson.teachers.set(teachers)
            lesson.locations.set(locations)
            lesson.session_times.set(session_times)
            cls.log_created(cls.__name__, lesson.pk, created)
            return lesson
        except EnumNotExistError as err:
            raise err
        except Exception as e:
            raise e

    def get_course_session_types(self) -> List[LessonTypeEnum]:
        session_types = set()
        for course_instance in Lesson.objects.filter(code=self.course.code):
            session_types.add(course_instance.lesson_type.enum)
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

    def get_teacher(self, index):
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
        return self.teachers.first()

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

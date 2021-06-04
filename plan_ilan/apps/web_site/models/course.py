import logging
from typing import List

from django.db import models
from django.db.models import Avg

from plan_ilan.exceptaions.enum_not_exist_error import EnumNotExistError
from . import BaseModel, LessonTime, Location, Teacher, LessonTypeEnum, Exam
from .enums import Department, Faculty, LessonType


class Course(BaseModel):
    code = models.CharField(primary_key=True, max_length=10, editable=False)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='courses')
    syllabus_link = models.URLField(null=True)
    exams = models.ManyToManyField(Exam, related_name='courses')

    class Meta:
        ordering = ['name']
        db_table = 'courses'

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
                                                           'faculty': faculty
                                                       })
        if created or exams:
            course.exams.set(exams)
        cls.log_created(course, created)
        if not created and not course.syllabus_link and syllabus_link:
            course.syllabus_link = syllabus_link
            course.save()
        return course

    def get_lessons(self):
        return self.lessons.all()

    @property
    def slug(self):
        return self.code

    @property
    def average_rating(self) -> float:
        return self.ratings.aggregate(average_value=Avg('value'))['average_value']

    @property
    def amount_of_ratings(self) -> int:
        return self.ratings.count()

    @property
    def total_points(self) -> float:
        return (self.lessons
                .exclude(lesson_type__in=[LessonTypeEnum.REINFORCING, LessonTypeEnum.MACHLAKA_TIME])
                .values('lesson_type', 'points')
                .distinct()
                .aggregate(models.Sum('points'))
                )['points__sum']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Lesson(BaseModel):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    group = models.CharField(max_length=3)
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE, related_name='lessons')
    details_link = models.URLField(null=True)
    teachers = models.ManyToManyField(Teacher, related_name='lessons')
    session_times = models.ManyToManyField(LessonTime, related_name='lessons')
    points = models.FloatField(null=True)
    locations = models.ManyToManyField(Location, related_name='lessons')

    class Meta:
        ordering = ['lesson_type', 'group']
        db_table = 'lessons'

    @classmethod
    def create(cls, code: str, group: str, name: str, teachers: List[Teacher], session_type: LessonType,
               faculty: Faculty, department: Department, session_times: List[LessonTime], locations: List[Location],
               exams: List[Exam], points: float = None, details_link: str = None,
               syllabus_link: str = None) -> 'Lesson':
        if not len(teachers) > 0:
            raise cls.generate_cant_create_model_err(cls.__name__, 'teachers', "staff list can't be empty")
        if not len(session_times) > 0:
            raise cls.generate_cant_create_model_err(cls.__name__, 'session_times',
                                                     "session_times list can't be empty")
        if not len(locations) >= 0:
            raise cls.generate_cant_create_model_err(cls.__name__, 'locations', "locations list can't be empty")
        try:
            course = Course.create(code, name, department, faculty, exams, syllabus_link)
            lesson_id = f'{code}_{group}_{session_times[0].year}'
            lesson, created = Lesson.objects.get_or_create(id=lesson_id,
                                                           defaults={
                                                               'course': course,
                                                               'group': group,
                                                               'lesson_type': session_type,
                                                               'details_link': details_link,
                                                               'points': points})
            lesson.teachers.set(teachers)
            if created or locations:
                lesson.locations.set(locations)
            lesson.session_times.set(session_times)
            cls.log_created(lesson, created)
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
            semesters.add(session_times.semester.choice)
        if len(semesters) != 1:
            if len(semesters) == 0:
                logging.warning('Course with no listed semesters')
            else:
                logging.warning('Course with more than one different semesters')
        return semesters.pop()

from dataclasses import dataclass, field

from PlanIlan.models import Course
from .base_dto import BaseDto
from .rating_dto import RatingDto
from .teacher_dto import TeacherDto


class CourseDto(BaseDto):
    code: str
    group_code: str
    name: str
    teacher: TeacherDto
    faculty: str
    semester: str
    details_link: str
    rating: RatingDto

    @property
    def mapping_options(self):
        return {
            # 'code': lambda course: course.code,
            # 'group_code': lambda course:course.group_code,
            'teacher': lambda course: TeacherDto.map(course.teacher),
            'faculty': lambda course: course.faculty.label,
            'semester': lambda course: course.semester.label,
            'details_link': lambda course: str(course.details_link),
            'rating': lambda course: RatingDto.map(course.rating)
        }

    @classmethod
    def maps_from(cls):
        return type(Course)

    @classmethod
    def maps_to(cls):
        return type(cls)



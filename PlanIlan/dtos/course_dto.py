from dataclasses import dataclass, field

from PlanIlan.models import Course
from .base_dto import BaseDto
from .rating_dto import RatingDto
from .teacher_dto import TeacherDto


class CourseDto(BaseDto):
    code: str = field(init=False)
    group_code: str = field(init=False)
    name: str = field(init=False)
    teacher: TeacherDto = field(init=False)
    faculty: str = field(init=False)
    semester: str = field(init=False)
    details_link: str = field(init=False)
    rating: RatingDto = field(init=False)

    @classmethod
    def mapping_options(self):
        return {
            # 'code': lambda course: course.code,
            # 'group_code': lambda course:course.group_code,
            'teacher': lambda course: TeacherDto.map(course.teacher),
            'faculty': lambda course: course.department.label,
            'semester': lambda course: course.semester.label,
            'details_link': lambda course: str(course.details_link),
            'rating': lambda course: RatingDto.map(course.rating)
        }

    @classmethod
    def maps_from(cls):
        return Course

    @classmethod
    def maps_to(cls):
        return cls

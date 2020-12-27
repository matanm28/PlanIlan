from .base_dto import BaseDto
from .teacher_dto import TeacherDto
from .rating_dto import RatingDto
from .lesson_time_dto import LessonTimeDto
from .location_dto import LocationDto
from .course_dto import CourseDto

TeacherDto.init_mapper()
RatingDto.init_mapper()
LessonTimeDto.init_mapper()
LocationDto.init_mapper()
CourseDto.init_mapper()

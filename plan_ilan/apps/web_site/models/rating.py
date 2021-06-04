from typing import Union

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from plan_ilan.utils.general import name_of
from . import BaseModel, Account, Course, Teacher

MIN_RATING, MAX_RATING = 0, 5
VALIDATORS = [MinValueValidator(MIN_RATING, f'Value should not fall short of {MIN_RATING}'),
              MaxValueValidator(MAX_RATING, f'Value should not exceed {MAX_RATING}')]


class Rating(BaseModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(validators=VALIDATORS)

    class Meta:
        ordering = ['value', 'pk']
        abstract = True

    @classmethod
    def create(cls, user: Account, value: int, ref_instance: Union[Teacher, Course]):
        if not isinstance(ref_instance, (Teacher, Course)):
            raise cls.generate_cant_create_model_err(name_of(cls), 'ref_instance', [name_of(Teacher), name_of(Course)],
                                                     name_of(ref_instance))
        rating_class = TeacherRating if isinstance(ref_instance, Teacher) else CourseRating
        rating = rating_class.create(user, value, ref_instance)
        rating.value = value
        rating.save()
        return rating

    def edit_rating(self, edited_value: int = None) -> bool:
        if edited_value is None:
            return False
        self.value = edited_value
        self.save()
        return True

    def __str__(self) -> str:
        return f'{self.value}'


class TeacherRating(Rating):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='ratings')

    class Meta:
        unique_together = ['teacher', 'user']
        db_table = 'teacher_ratings'

    @classmethod
    def create(cls, user: Account, value: int, teacher: Teacher) -> 'TeacherRating':
        rating, created = TeacherRating.objects.get_or_create(user=user, teacher=teacher, defaults={"value": value})
        cls.log_created(rating, created)
        return rating


class CourseRating(Rating):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')

    class Meta:
        unique_together = ['course', 'user']
        db_table = 'course_ratings'

    @classmethod
    def create(cls, user: Account, value: int, course: Course) -> 'CourseRating':
        rating, created = CourseRating.objects.get_or_create(user=user, course=course, defaults={"value": value})
        cls.log_created(rating, created)
        return rating

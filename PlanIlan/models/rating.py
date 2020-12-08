from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from PlanIlan.models import Teacher, Course, BaseModel

MIN_RATING, MAX_RATING = 0, 5
VALIDATORS = [MinValueValidator(MIN_RATING, f'Value should not fall short of {MIN_RATING}'),
              MaxValueValidator(MAX_RATING, f'Value should not exceed {MAX_RATING}')]


class Rating(BaseModel):
    average = models.IntegerField(null=True, default=None, validators=VALIDATORS)
    amount_of_raters = models.IntegerField(default=0,
                                           validators=[MinValueValidator(0, 'Value has to be a natural number')])

    class Meta:
        abstract = True

    @classmethod
    def create(cls, rated_instance) -> 'Rating':
        if isinstance(rated_instance, Teacher):
            return TeacherRating(average=None, teacher=rated_instance)
        elif isinstance(rated_instance, Course):
            return CourseRating(average=None, course=rated_instance)
        else:
            return None

    def update_rating(self, new_rating: int, save=True):
        if self.amount_of_raters == 0:
            self.average = new_rating
        else:
            self.average = ((self.average * self.amount_of_raters) + new_rating) / (self.amount_of_raters + 1)
        self.amount_of_raters += 1
        if save:
            self.save()


class TeacherRating(Rating):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)


class CourseRating(Rating):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

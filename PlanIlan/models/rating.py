from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from PlanIlan.models import BaseModel

MIN_RATING, MAX_RATING = 0, 5
VALIDATORS = [MinValueValidator(MIN_RATING, f'Value should not fall short of {MIN_RATING}'),
              MaxValueValidator(MAX_RATING, f'Value should not exceed {MAX_RATING}')]


class Rating(BaseModel):
    average = models.FloatField(null=True, default=None, validators=VALIDATORS)
    amount_of_raters = models.IntegerField(default=0,
                                           validators=[MinValueValidator(0, 'Value has to be a natural number')])

    @classmethod
    def create(cls, average: float = None, amount_of_raters: int = 0) -> 'Rating':
        rating = Rating(average=average, amount_of_raters=amount_of_raters)
        rating.save()
        return rating

    def __str__(self):
        return str(self.average)

        # class Meta:

    #     abstract = True

    # @classmethod
    # def create_without_save(cls, rated_instance) -> 'Rating':
    #     if isinstance(rated_instance, Teacher):
    #         return TeacherRating(average=None, teacher=rated_instance)
    #     elif isinstance(rated_instance, Course):
    #         return CourseRating(average=None, course=rated_instance)
    #     else:
    #         return None

    def update_rating(self, new_rating: int, save=True):
        if self.amount_of_raters in None:
            self.average = new_rating
        else:
            self.average = ((self.average * self.amount_of_raters) + new_rating) / (self.amount_of_raters + 1)
        self.amount_of_raters += 1
        if save:
            self.save()

# class TeacherRating(Rating):
#     teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
#
#
# class CourseRating(Rating):
#     course = models.ForeignKey('Course', on_delete=models.CASCADE)

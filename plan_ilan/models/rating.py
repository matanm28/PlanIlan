from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MIN_RATING, MAX_RATING = 0, 5
VALIDATORS = [MinValueValidator(MIN_RATING, f'Value should not fall short of {MIN_RATING}'),
              MaxValueValidator(MAX_RATING, f'Value should not exceed {MAX_RATING}')]


class Rating(models.Model):
    average = models.IntegerField(validators=VALIDATORS)
    amount_of_raters = models.IntegerField(default=0,
                                           validators=[MinValueValidator(0, 'Value has to be a natural number')])

    class Meta:
        abstract = True


class TeacherRating(Rating):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)


class CourseRating(Rating):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

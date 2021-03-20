import django_filters
from django_filters import *
from django_filters.widgets import BooleanWidget

from .models import *


class CourseInstanceFilter(django_filters.FilterSet):
    name = CharFilter(field_name='course__name', lookup_expr='icontains')
    locations__online = BooleanFilter(widget=BooleanWidget())
    rating = ChoiceFilter(choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')),
                          field_name='course__rating__average')
    start_time = TimeFilter(field_name='session_times__start_time', lookup_expr='gt')
    end_time = TimeFilter(field_name='session_times__end_time', lookup_expr='lt')
    TEACHER_CHOICES = [
        (i, t) for i, t in enumerate(Teacher.objects.all())
    ]
    teachers = ChoiceFilter(field_name='teachers', choices=TEACHER_CHOICES)

    class Meta:
        model = CourseInstance
        fields = ['teachers']

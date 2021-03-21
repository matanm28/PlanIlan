import django_filters
from django import forms
from django_filters import *
from django_filters.widgets import BooleanWidget

from .models import *

RATING_CHOICES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5')
]

DAY_CHOICES = [
    (1, 'א'),
    (2, 'ב'),
    (3, 'ג'),
    (4, 'ד'),
    (5, 'ה'),
    (6, 'ו'),
]

SEMESTER_CHOICES = [
    (1, 'א'),
    (2, 'ב'),
]

SESSION_CHOICES = [
    (0, 'הרצאה'),
    (1, 'תרגול'),
    (2, 'תגבור'),
    (3, 'סמינריון'),
    (4, 'חברותא'),
    (5, 'סדנה'),
]


class CourseInstanceFilter(django_filters.FilterSet):
    name = CharFilter(field_name='course__name', lookup_expr='icontains')
    online = BooleanFilter(field_name='locations__online', widget=BooleanWidget())
    rating_from = ChoiceFilter(choices=RATING_CHOICES, field_name='course__rating__average', lookup_expr='gt')
    rating_to = ChoiceFilter(choices=RATING_CHOICES, field_name='course__rating__average', lookup_expr='lt')
    start_time = TimeFilter(field_name='session_times__start_time', lookup_expr='gt')
    end_time = TimeFilter(field_name='session_times__end_time', lookup_expr='lt')
    teachers = ModelChoiceFilter(queryset=Teacher.objects.all())
    day = MultipleChoiceFilter(field_name='session_times___day', choices=DAY_CHOICES,
                               widget=forms.SelectMultiple(attrs={"class": "form-control"}))
    semester = MultipleChoiceFilter(field_name='session_times___semester', choices=SEMESTER_CHOICES,
                                    widget=forms.SelectMultiple(attrs={"class": "form-control"}))
    session_type = ChoiceFilter(field_name='_session_type', choices=SESSION_CHOICES)

    class Meta:
        model = CourseInstance
        fields = ['teachers']

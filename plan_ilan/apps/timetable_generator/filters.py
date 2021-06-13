import django_filters
from django import forms
from django_filters import *

from plan_ilan.apps.web_site.models import Lesson, DepartmentEnum, SemesterEnum


class TimeTableFilter(django_filters.FilterSet):
    department = MultipleChoiceFilter(field_name='course__department', choices=DepartmentEnum.choices,
                                      widget=forms.SelectMultiple(attrs={"class": "form-control"}))
    semester = ChoiceFilter(field_name='session_times__semester', choices=SemesterEnum.choices)

    class Meta:
        model = Lesson
        fields = '__all__'

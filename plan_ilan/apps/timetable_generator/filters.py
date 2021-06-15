import django_filters
from django import forms
from django_filters import *

from plan_ilan.apps.web_site.models import DepartmentEnum, SemesterEnum, Course, Department


class TimeTableFilter(django_filters.FilterSet):
    department = ModelMultipleChoiceFilter(queryset=Department.objects.all(),
                                           widget=forms.CheckboxSelectMultiple)
    semester = ChoiceFilter(field_name='lessons__session_times__semester', choices=SemesterEnum.choices)

    class Meta:
        model = Course
        fields = ['department','semester']

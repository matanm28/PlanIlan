import django_filters
from django_filters.widgets import BooleanWidget

from .models import *
from django_filters import *
from django import forms


class CourseFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    locations__online = BooleanFilter(widget=BooleanWidget())

    class Meta:
        model = Course
        fields = ['name', 'rating', 'teachers']

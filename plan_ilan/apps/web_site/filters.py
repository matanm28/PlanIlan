import django_filters
from django import forms
from django.db.models.aggregates import Avg
from django_filters import *
from django_filters.widgets import BooleanWidget
from django.utils.translation import gettext as _

from plan_ilan.apps.web_site.models import *

RATING_CHOICES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5')
]

ONLINE_COICHES = [
    ('0', 'Yes'),
    ('1', 'No'),
    ('', 'Any')
]


class MyBooleanWidget(BooleanWidget):
    def __init__(self, attrs=None):
        choices = (('', _('מקוון?')),
                   ('true', _('כן')),
                   ('false', _('לא')))
        super(BooleanWidget, self).__init__(attrs, choices)


class CourseInstanceFilter(django_filters.FilterSet):
    department = ChoiceFilter(field_name='course__department', choices=Department.choices(), empty_label='מחלקה',
                              widget=forms.Select(
                                  attrs={'style': 'width:50%; text-align: center; border-radius: 5px;'}))
    name = CharFilter(field_name='course__name', lookup_expr='icontains', widget=forms.TextInput(
        attrs={'placeholder': "שם הקורס...",
               'style': 'width:fit-content; text-align: center; border-radius: 5px;'}))
    online = BooleanFilter(field_name='locations__online',
                           widget=MyBooleanWidget(
                               attrs={'style': 'width:fit-content; text-align: center; border-radius: 5px;'}))
    start_time = TimeFilter(field_name='session_times__start_time', lookup_expr='gt')
    end_time = TimeFilter(field_name='session_times__end_time', lookup_expr='lt')
    teachers = CharFilter(field_name='teachers__name', lookup_expr='icontains', widget=forms.TextInput(
        attrs={'placeholder': "שם המרצה/המתרגל...",
               'style': 'width:fit-content; text-align: center; border-radius: 5px;'}))
    day = MultipleChoiceFilter(field_name='session_times__day', choices=Day.choices(),
                               widget=forms.SelectMultiple(attrs={"class": "form-control", "style": "height:auto"}))
    semester = MultipleChoiceFilter(field_name='session_times__semester', choices=SemesterEnum.choices,
                                    widget=forms.SelectMultiple(
                                        attrs={"class": "form-control", "style": "height:auto"}))
    session_type = ChoiceFilter(field_name='lesson_type', choices=LessonType.choices().order_by('label'), empty_label='סוג השיעור',
                                widget=forms.Select(
                                    attrs={'style': 'width:fit-content; text-align: center; border-radius: 5px;'}))
    ratings = ChoiceFilter(field_name='course__ratings__value', choices=RATING_CHOICES, method='filter_ratings',
                           empty_label='דירוג החל מ...', widget=forms.Select(
            attrs={'style': 'width:fit-content; text-align: center; border-radius: 5px;'}))

    def filter_ratings(self, queryset, name, value):
        return queryset.annotate(avg_rating=Avg(name)).filter(avg_rating__gte=value)

    class Meta:
        model = Lesson
        fields = '__all__'


class TeacherInstanceFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains', widget=forms.TextInput(
        attrs={'placeholder': "שם המרצה/המתרגל...",
               'style': 'width:fit-content; text-align: center; border-radius: 5px;'}))
    faculty = ChoiceFilter(field_name='faculty', choices=Faculty.choices(), empty_label="פקולטה...",
                           widget=forms.Select(
                               attrs={'style': 'width:fit-content; text-align: center; border-radius: 5px;'}))
    ratings = ChoiceFilter(field_name='ratings__value', choices=RATING_CHOICES, method='filter_ratings',
                           empty_label='דירוג החל מ...', widget=forms.Select(
            attrs={'style': 'width:fit-content; text-align: center; border-radius: 5px;'}))

    def filter_ratings(self, queryset, name, value):
        return queryset.annotate(avg_rating=Avg(name)).filter(avg_rating__gte=value)

    class Meta:
        model = Teacher
        fields = ['name', 'faculty']

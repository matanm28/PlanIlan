from django.urls import path, register_converter

from plan_ilan.apps.timetable_generator import views, converters

register_converter(converters.CommaSeparatedIntegerListConverter, 'int_list')

urlpatterns = [
    path(r'^timetable/', views.FirstView.as_view(), name='first-form'),
    path(r'^timetable/deps', views.PickDepartmentsView.as_view(), name='pick-deps'),
    path(r'^timetable/courses$', views.pick_courses, name='pick-courses'),
    path(r'^timetable/lessons', views.pick_lessons, name="pick-lessons"),
    path(r'^timetable/build', views.build_timetable, name="build-timetable")
]

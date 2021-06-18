from django.urls import path

from plan_ilan.apps.timetable_generator import views

urlpatterns = [
    path('timetable/', views.first_form, name='first-form'),
    path('timetable/deps', views.pick_departments, name='pick-deps'),
    path('timetable/courses', views.pick_courses, name='pick-courses'),
    path('timetable/lessons', views.pick_lessons, name="pick-lessons"),
    path('timetable/build', views.build_timetable, name="build-timetable")
]

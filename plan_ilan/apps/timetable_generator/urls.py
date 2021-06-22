from django.urls import path, register_converter, re_path

from plan_ilan.apps.timetable_generator import views

urlpatterns = [
    path('timetable/', views.FirstView.as_view(), name='first-form'),
    path('timetable/deps', views.PickDepartmentsView.as_view(), name='pick-deps'),
    path('timetable/courses', views.pick_courses, name='pick-courses'),
    path('timetable/lessons', views.pick_lessons, name="pick-lessons"),
    path('timetable/build', views.build_timetable, name="build-timetable")
]

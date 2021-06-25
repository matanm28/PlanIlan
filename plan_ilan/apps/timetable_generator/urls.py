from django.urls import path, register_converter, re_path

from plan_ilan.apps.timetable_generator import views

urlpatterns = [
    path('timetable/', views.FirstView.as_view(), name='first-form'),
    path('timetable/deps', views.PickDepartmentsView.as_view(), name='pick-deps'),
    path('timetable/courses', views.PickCoursesView.as_view(), name='pick-courses'),
    path('timetable/lessons', views.PickLessonsView.as_view(), name='pick-lessons'),
    path('timetable/build', views.BuildTimeTableView.as_view(), name='build-timetable')
]

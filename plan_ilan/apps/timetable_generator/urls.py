from django.urls import path

from plan_ilan.apps.timetable_generator import views

urlpatterns = [
    path('timetable/', views.time_table, name='timetable'),
]

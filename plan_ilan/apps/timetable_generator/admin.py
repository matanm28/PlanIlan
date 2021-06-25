from django.contrib import admin
from .models import Timetable, TimetableSolution, RankedLesson

admin.register(RankedLesson)
admin.register(TimetableSolution)
admin.register(Timetable)

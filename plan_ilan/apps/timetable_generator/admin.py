from django.contrib import admin
from .models import Timetable, TimetableSolution, RankedLesson
from .models.timetable import TimetableCommonInfo


@admin.register(RankedLesson)
class RankedLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'rank')
    sortable_by = ('id', 'lesson', 'rank')


@admin.register(TimetableCommonInfo)
class TimetableCommonInfoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'account', 'name', 'semester')
    sortable_by = ('pk', 'account', 'name', 'semester')
    list_filter = ('semester',)


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('pk', 'common_info', 'max_num_of_days', 'is_done')
    sortable_by = ('pk', 'common_info', 'max_num_of_days', 'is_done')


@admin.register(TimetableSolution)
class TimetableSolutionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'common_info', 'score', 'iterations', 'is_solved', 'possibly_invalid')
    sortable_by = ('pk', 'score', 'iterations', 'is_solved', 'possibly_invalid')
    list_filter = ('is_solved', 'possibly_invalid')

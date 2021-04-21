from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django_admin_multiple_choice_list_filter.list_filters import MultipleChoiceListFilter

from .models import *

# Register your models here.
from .models.enums import EnumModel

admin.site.register(UserModel)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(CoursePost)
admin.site.register(TeacherPost)
admin.site.register(Location)
admin.site.register(SessionTime)
admin.site.register(Rating)
admin.site.register(Exam)


class LessonTypeListFilter(MultipleChoiceListFilter):
    title = _('Lesson Type')
    parameter_name = 'lesson_type__in'

    def lookups(self, request, model_admin: admin.ModelAdmin):
        return LessonTypeEnum.choices


class DayListFilter(MultipleChoiceListFilter):
    title = _('Day')
    parameter_name = 'session_times__day__in'

    def lookups(self, request, model_admin: admin.ModelAdmin):
        return DAYS.choices


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'group', 'lesson_type', 'points', 'has_details_link')
    list_filter = (LessonTypeListFilter,DayListFilter)

    @admin.display(description='Has Details', boolean=True)
    def has_details_link(self, obj: Lesson) -> bool:
        return obj.details_link is not None


# Enums
@admin.register(Faculty, Title, LessonType, ExamPeriod, Department, Semester)
class EnumAdmin(admin.ModelAdmin):
    list_display = ('number', 'label')


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ('number', 'label', 'full_label')

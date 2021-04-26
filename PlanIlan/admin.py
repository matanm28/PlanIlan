from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django_admin_multiple_choice_list_filter.list_filters import MultipleChoiceListFilter

from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(CoursePost)
admin.site.register(TeacherPost)
admin.site.register(Rating)


class LessonTypeListFilter(MultipleChoiceListFilter):
    title = _('Lesson Type')
    parameter_name = 'lesson_type__in'

    def lookups(self, request, model_admin: admin.ModelAdmin):
        return LessonTypeEnum.choices


class DayListFilterBase(MultipleChoiceListFilter):
    title = _('Day')

    def lookups(self, request, model_admin: admin.ModelAdmin):
        return DAYS.choices


class LessonDayListFilter(DayListFilterBase):
    parameter_name = 'session_times__day__in'


class LessonHasDetailsLinkFilter(admin.SimpleListFilter):
    LOOKUP_CHOICES = (('with_details_link', _('Yes')),
                      ('without_details_link', _('No')))
    title = _('Has Details')

    parameter_name = 'details_link'

    def lookups(self, request, model_admin):
        return self.LOOKUP_CHOICES

    def queryset(self, request, queryset: QuerySet):
        if self.value() == 'with_details_link':
            return queryset.filter(details_link__isnull=False)
        if self.value() == 'without_details_link':
            return queryset.filter(details_link__isnull=True)


class LessonHasSyllabusLinkFilter(admin.SimpleListFilter):
    LOOKUP_CHOICES = (('with_syllabus_link', _('Yes')),
                      ('without_syllabus_link', _('No')))
    title = _('Has Syllabus Link')

    parameter_name = 'syllabus_link'

    def lookups(self, request, model_admin):
        return self.LOOKUP_CHOICES

    def queryset(self, request, queryset: QuerySet):
        if self.value() == 'with_syllabus_link':
            return queryset.filter(course__syllabus_link__isnull=False)
        if self.value() == 'without_syllabus_link':
            return queryset.filter(course__syllabus_link__isnull=True)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'group', 'lesson_type', 'points', 'has_syllabus_link', 'has_details_link')
    sortable_by = ('name', 'group', 'lesson_type', 'points')
    list_filter = (LessonTypeListFilter, LessonDayListFilter, LessonHasSyllabusLinkFilter, LessonHasDetailsLinkFilter)

    @admin.display(description='Has Details', boolean=True)
    def has_details_link(self, obj: Lesson) -> bool:
        return obj.details_link is not None

    @admin.display(description='Has syllabus Link', boolean=True)
    def has_syllabus_link(self, obj: Lesson) -> bool:
        return obj.course.syllabus_link is not None


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'faculty', 'has_syllabus_link', 'rating_field')
    sortable_by = ('pk', 'name', 'code', 'department', 'faculty', 'has_syllabus_link', 'rating')
    exclude = ('exams', 'rating')
    list_filter = ('faculty',)

    @admin.display(description='Has syllabus Link', boolean=True)
    def has_syllabus_link(self, obj: Course) -> bool:
        return obj.syllabus_link is not None

    @admin.display(description='Rating', empty_value='-Not-Rated-')
    def rating_field(self, obj: Course) -> Rating:
        return obj.rating


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('pk', 'exam_date', 'exam_time', 'period', 'number_of_courses')
    sortable_by = ('pk',)
    list_filter = ('period',)
    ordering = ['pk']

    @admin.display(description='Number of Courses')
    def number_of_courses(self, obj: Exam) -> int:
        return obj.courses.count()

    @admin.display(description='Date')
    def exam_date(self, obj: Exam) -> int:
        return obj.date.strftime('%d.%m.%y')

    @admin.display(description='Time')
    def exam_time(self, obj: Exam) -> int:
        return obj.date.strftime('%H:%M')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'building_name', 'building_number', 'class_number', 'is_online_location', 'lessons_in_location')
    sortable_by = ('pk', 'building_name', 'building_number', 'class_number')
    ordering = ['building_number', 'class_number']

    @admin.display(description='Online', boolean=True)
    def is_online_location(self, obj: Location):
        return obj.is_zoom_class

    @admin.display(description='Lessons in location')
    def lessons_in_location(self, obj: Location) -> int:
        return obj.lessons.count()


@admin.register(LessonTime)
class LessonTimeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'day', 'start_time', 'end_time', 'semester', 'year', 'lessons_using_time')
    sortable_by = ('pk', 'day', 'start_time', 'end_time', 'semester', 'year')
    list_filter = ('day', 'semester')
    ordering = ['day', 'start_time', 'end_time', 'year']

    @admin.display(description='Lessons using time')
    def lessons_using_time(self, obj: LessonTime) -> int:
        return obj.lessons.count()


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'title', 'faculty', 'phone', 'email', 'office', 'website_url', 'rating')
    sortable_by = ('pk', 'name', 'title', 'faculty')
    list_filter = ('title', 'faculty')
    ordering = ('name', 'faculty', 'pk')


# Enums
@admin.register(Faculty, Title, LessonType, ExamPeriod, Department, Semester)
class EnumAdmin(admin.ModelAdmin):
    list_display = ('number', 'label')
    sortable_by = ('number', 'label')


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ('number', 'label', 'full_label')

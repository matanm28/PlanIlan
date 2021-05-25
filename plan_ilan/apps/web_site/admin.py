from django.contrib import admin
from django.db.models import QuerySet, Avg
from django.utils.translation import gettext_lazy as _
from django_admin_multiple_choice_list_filter.list_filters import MultipleChoiceListFilter
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from plan_ilan.apps.web_site.models import *


# Register your models here.


class FacultyListFilter(MultipleChoiceListFilter):
    title = _('Faculty')
    parameter_name = 'faculty__in'

    def lookups(self, request, model_admin: admin.ModelAdmin):
        return FacultyEnum.choices


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
    search_fields = ('course__name', 'course__code', 'group', 'lesson_type__label')
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
    sortable_by = ('name', 'code', 'department', 'faculty', 'has_syllabus_link', 'rating')
    search_fields = ('name', 'code', 'department__label', 'faculty__label')
    exclude = ('exams', 'rating')
    list_filter = ('faculty',)

    @admin.display(description='Has syllabus Link', boolean=True)
    def has_syllabus_link(self, obj: Course) -> bool:
        return obj.syllabus_link is not None

    @admin.display(description='Rating', empty_value='-Not-Rated-')
    def rating_field(self, obj: Course) -> float:
        return obj.ratings.aggregate(average_value=Avg('value'))['average_value']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam_date', 'exam_time', 'period', 'number_of_courses')
    sortable_by = ('id', 'exam_date',)
    list_filter = ('period',)
    ordering = ['id']

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
    list_display = ('id', 'building_name', 'building_number', 'class_number', 'is_online_location', 'lessons_in_location')
    sortable_by = ('id', 'building_name', 'building_number', 'class_number')
    search_fields = ('building_name', 'building_number', 'class_number')
    ordering = ['building_number', 'class_number']

    @admin.display(description='Online', boolean=True)
    def is_online_location(self, obj: Location):
        return obj.is_zoom_class

    @admin.display(description='Lessons in location')
    def lessons_in_location(self, obj: Location) -> int:
        return obj.lessons.count()


@admin.register(LessonTime)
class LessonTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'start_time', 'end_time', 'semester', 'year', 'lessons_using_time')
    sortable_by = ('id', 'day', 'start_time', 'end_time', 'semester', 'year')
    list_filter = ('day', 'semester')
    ordering = ['day', 'start_time', 'end_time', 'year']

    @admin.display(description='Lessons using time')
    def lessons_using_time(self, obj: LessonTime) -> int:
        return obj.lessons.count()


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'title', 'faculty', 'phone', 'email', 'office', 'website_url', 'rating_field')
    sortable_by = ('id', 'name', 'title', 'faculty')
    search_fields = ('name', 'faculty__label')
    list_filter = ('title', FacultyListFilter)
    ordering = ('name', 'faculty', 'id')

    @admin.display(description='Rating', empty_value='-Not-Rated-')
    def rating_field(self, obj: Teacher) -> Rating:
        return obj.ratings.aggregate(average_value=Avg('value'))['average_value']


# Enums
@admin.register(Faculty, Title, LessonType, ExamPeriod, Department, Semester)
class EnumAdmin(admin.ModelAdmin):
    list_display = ('number', 'label')
    sortable_by = ('number', 'label')


@admin.register(Day)
class DayAdmin(EnumAdmin):
    list_display = ('number', 'label', 'full_label')


class ReviewChildAdmin(PolymorphicChildModelAdmin):
    base_model = Review
    list_display = ('id', 'author', 'headline', 'slug', 'date_created', 'date_modified', 'likes_count')
    exclude = ('slug',)
    sortable_by = ('id', 'date_created', 'date_modified')
    search_fields = ('author__username', 'headline')
    ordering = ('date_modified', 'date_created')

    @admin.display(description='likes')
    def likes_count(self, obj: Review) -> int:
        return obj.likes.count()


@admin.register(CourseReview)
class CourseReviewAdmin(ReviewChildAdmin):
    base_model = CourseReview


@admin.register(TeacherReview)
class TeacherReviewAdmin(ReviewChildAdmin):
    base_model = TeacherReview


@admin.register(Review)
class ReviewAdmin(PolymorphicParentModelAdmin):
    base_model = Review
    child_models = (CourseReview, TeacherReview)
    list_filter = (PolymorphicChildModelFilter,)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'faculty', 'date_joined', 'last_login')
    sortable_by = ('id', 'faculty',)
    ordering = ('user__date_joined', 'user__last_login')
    list_filter = (FacultyListFilter,)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'review_id', 'date_created', 'date_modified')
    sortable_by = ('id', 'date_created', 'date_modified')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'text')
    ordering = ('date_modified', 'date_created')

    @admin.display(description='review id')
    def review_id(self, obj: Reply) -> int:
        return obj.review.pk


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'review_id')

    @admin.display(description='user id')
    def user_id(self, obj: Like) -> int:
        return obj.user.pk

    @admin.display(description='review id')
    def review_id(self, obj: Like) -> int:
        return obj.review.pk


@admin.register(TeacherRating, CourseRating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'value')
    sortable_by = ('id', 'user', 'value')

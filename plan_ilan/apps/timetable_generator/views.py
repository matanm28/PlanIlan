from django.shortcuts import render

from plan_ilan.apps.web_site.decorators import authenticated_user
from plan_ilan.apps.web_site.models import Lesson, Course, Teacher, LessonTime
from django.core import serializers
from plan_ilan.apps.web_site.filters import CourseInstanceFilter, TeacherInstanceFilter
from django.http import JsonResponse


@authenticated_user
def time_table(request):
    if request.method == 'GET':
        lessons_list = Lesson.objects.all()
        lesson_filter = CourseInstanceFilter(request.GET, queryset=lessons_list)
        lessons_list = lesson_filter.qs
        context = {'lesson_filter': lesson_filter}
        if request.is_ajax():
            lessons_pk = list(map(lambda lesson: lesson.pk, lessons_list))
            course_list = Course.objects.filter(lessons__pk__in=lessons_pk).distinct()
            teacher_list = Teacher.objects.filter(lessons__pk__in=lessons_pk).distinct()
            session_list = LessonTime.objects.filter(lessons__pk__in=lessons_pk)
            json_session_list = serializers.serialize("json", session_list)
            json_teacher_list = serializers.serialize("json", teacher_list)
            json_course_list = serializers.serialize("json", course_list)
            json_lesson_list = serializers.serialize("json", lessons_list)
            context = {'json_lesson_list': json_lesson_list,
                       'json_course_list': json_course_list,
                       'json_teacher_list': json_teacher_list,
                       'json_session_list': json_session_list}
            return JsonResponse(context, safe=False)
        return render(request, 'timetable_generator/timetable.html', context)
    return render(request, 'timetable_generator/timetable.html')

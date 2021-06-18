from django.shortcuts import render, get_object_or_404

from plan_ilan.apps.web_site.decorators import authenticated_user
from plan_ilan.apps.web_site.models import Lesson, Course, Account, Department, Semester
from .models import RankedLesson, Timetable


@authenticated_user
def first_form(request):
    context = {'semesters': Semester.objects.all()}
    return render(request, 'timetable_generator/first_form.html', context)


@authenticated_user
def pick_departments(request):
    semester = get_object_or_404(Semester, label=request.GET.get('semester'))
    table_name = request.GET.get('table-name')
    learn_days = int(request.GET.get('week-days'))
    user = get_object_or_404(Account, user=request.user)
    timetable_user = Timetable.temporal_create(account=user, name=table_name, semester=semester,
                                               max_num_of_days=learn_days)
    timetable_user.save()
    context = {"departments": Department.choices()}
    return render(request, 'timetable_generator/pick_deps.html', context)


@authenticated_user
def pick_courses(request):
    timetable_user = Timetable.objects.filter(common_info__account=Account.objects.get(user=request.user)).first()
    course_elective = Course.objects.filter(department__in=request.POST.getlist("mandatory-deps"),
                                            lessons__session_times__semester=timetable_user.semester)
    course_mandatory = Course.objects.filter(department__in=request.POST.getlist("elective-deps"),
                                             lessons__session_times__semester=timetable_user.semester)
    context = {"course_elective": course_elective, "course_mandatory": course_mandatory}
    return render(request, 'timetable_generator/pick_courses.html', context)


@authenticated_user
def pick_lessons(request):
    mand_courses = request.POST.getlist("mand")
    mand_list = Course.objects.filter(pk__in=mand_courses)
    elect_courses = request.POST.getlist("elect")
    elect_list = Course.objects.filter(pk__in=elect_courses)
    context = {"mand_list": mand_list, "elect_list": elect_list}
    return render(request, 'timetable_generator/pick_lessons.html', context)


@authenticated_user
def build_timetable(request):
    selected_mand_lessons = request.POST.getlist("mand-lessons")
    ranks_mand = request.POST.getlist("rank-mand-lesson")
    mand_lessons = Lesson.objects.select_related("course").filter(pk__in=selected_mand_lessons)
    selected_elect_lessons = request.POST.getlist("elect-lessons")
    ranks_elect = request.POST.getlist("rank-elect-lesson")
    elect_lessons = Lesson.objects.select_related("course").filter(pk__in=selected_elect_lessons)
    ranked_mand = [RankedLesson.create(lesson, rank) for (lesson, rank) in zip(mand_lessons, ranks_mand)]
    ranked_elect = [RankedLesson.create(lesson, rank) for (lesson, rank) in zip(elect_lessons, ranks_elect)]
    return render(request, 'timetable_generator/build_timetable.html')

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .decorators import unauthenticated_user, authenticated_user
from .filters import *
from .forms import CreateAccountForm, CreateDjangoUserForm
from .models import *


# @login_required(login_url='')


def search(request):
    if request.method == 'GET':
        # COURSE SEARCH ENGINE
        lessons = Lesson.objects.all()
        lesson_filter = CourseInstanceFilter(request.GET, queryset=lessons)
        lessons = lesson_filter.qs
        lessons_pk = list(map(lambda lesson: lesson.pk, lessons))
        courses = Course.objects.filter(lessons__pk__in=lessons_pk).distinct()
        # TEACHER SEARCH ENGINE
        teachers = Teacher.objects.all()
        teacher_filter = TeacherInstanceFilter(request.GET, queryset=teachers)
        teachers = teacher_filter.qs

        departments = Department.objects.all()
        context = {'lesson_filter': lesson_filter, 'lessons': lessons, 'courses': courses,
                   'teacher_filter': teacher_filter, 'teachers': teachers, 'departments': departments}
        return render(request, 'PlanIlan/search.html', context)
    return render(request, 'PlanIlan/search.html')


def home(request):
    # todo: get last staff and courses
    # todo: save them in data structure
    # TEACHER BEST RATINGS VIEW
    teachers_obj = [Teacher.objects.get(name="ארז שיינר"),
                    Teacher.objects.get(name="יורם לוזון")]
    # COURSES BEST RATING VIEW
    courses_obj = [Course.objects.get(code="89550"), Course.objects.get(code="88218")]
    # LATEST COMMENTS
    teacher_comments = TeacherReview.objects.all().order_by('date_modified')[:5]
    course_comments = CourseReview.objects.all().order_by('date_modified')[:5]
    context = {'teachers': teachers_obj, 'courses_obj': courses_obj,
               'teacher_comments': teacher_comments, 'course_comments': course_comments}
    if request.method == 'GET':
        if request.is_ajax():
            all_likes = Like.objects.filter(user=Account.objects.get(user=request.user))
            json_likes_list = serializers.serialize("json", all_likes)
            return JsonResponse({'json_likes_list': json_likes_list}, safe=False)
        return render(request, 'PlanIlan/home.html', context)
    elif request.method == 'POST':
        if request.POST.get('PostID', ''):
            if request.POST.get('type', '') == 'course':
                course_post = CourseReview.objects.get(id=request.POST.get('PostID', ''))
                if request.POST.get('to_add', '') == '1':
                    course_post.like_review(Account.objects.get(user=request.user))
                else:
                    course_post.remove_like(Account.objects.get(user=request.user))
                course_post.save()
            else:
                teacher_post = TeacherReview.objects.get(id=request.POST.get('PostID', ''))
                teacher_post.like_review(request.user)
                teacher_post.save()
            return render(request, 'PlanIlan/home.html', context)
        elif request.POST.get('Rating_course_ID', ''):
            course_id = Lesson.objects.get(id=request.POST.get('Rating_course_ID', ''))
            course_id.course.rating.update_rating(int(request.POST.get('rate_number', '')))
    return render(request, 'PlanIlan/home.html')


@unauthenticated_user
def register(request):
    if request.method == 'POST':
        django_user_form = CreateDjangoUserForm(request.POST)
        account_form = CreateAccountForm(request.POST)
        if django_user_form.is_valid() and account_form.is_valid():
            user = django_user_form.save()
            account = account_form.save(commit=False)
            account.user = user
            account.save()
            # messages.success(request, 'ההרשמה נקלטה בהצלחה')
            login(request, user)
            return redirect('home')
        else:
            context = {'form': django_user_form, 'account_form': account_form}
            return render(request, 'PlanIlan/register.html', context)
    django_user_form = CreateDjangoUserForm()
    account_form = CreateAccountForm()
    context = {'form': django_user_form, 'account_form': account_form}
    return render(request, 'PlanIlan/register.html', context)


@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_ = authenticate(request, username=username, password=password)
        if user_ is not None:
            login(request, user_)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')
    return render(request, 'PlanIlan/login.html')


def logout_user(request):
    logout(request)
    return redirect('home')


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
        return render(request, 'PlanIlan/timetable.html', context)
    return render(request, 'PlanIlan/timetable.html')

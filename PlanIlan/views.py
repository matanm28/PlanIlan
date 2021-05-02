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
        courses = Course.objects.all()
        course_filter = CourseFilter(request.GET, queryset=courses)
        courses = course_filter.qs
        # TEACHER SEARCH ENGINE
        teachers = Teacher.objects.all()
        teacher_filter = TeacherInstanceFilter(request.GET, queryset=teachers)
        teachers = teacher_filter.qs
        context = {'course_filter': course_filter, 'courses': courses,
                   'teacher_filter': teacher_filter, 'teachers': teachers}
        return render(request, 'PlanIlan/search.html', context)
    return render(request, 'PlanIlan/search.html')


def home(request):
    # todo: get last staff and courses
    # todo: save them in data structure
    # TEACHER BEST RATINGS VIEW
    teachers_obj = [Teacher.objects.get(name="ארז שיינר"),
                    Teacher.objects.get(name="יורם לוזון")]
    # COURSES BEST RATING VIEW
    # courses_obj = [Course.objects.get(name=""),
    #                Course.objects.get(name="מבוא למדעי החיים")]
    courses_obj = [Course.objects.get(code="89550"), Course.objects.get(code="88218")]

    # LATEST COMMENTS
    teacher_comments = TeacherReview.objects.all().order_by('date_modified')
    context = {'teachers': teachers_obj, 'courses_obj': courses_obj,
               'teacher_comments': teacher_comments}
    if request.method == 'GET':
        # courses_obj = [Course.objects.get(code="76786"), Course.objects.get(code="77837")]
        # teachers_obj = [Teacher.objects.get(name="ארז שיינר"), Teacher.objects.get(name="גל קמינקא")]
        # teachers_obj = [Teacher.objects.get(name="ארז שיינר"), Teacher.objects.get(name="יורם לוזון"), Teacher.objects.get(name="גיל אריאל")]
        context = {'staff': teachers_obj,
                   'courses': courses_obj}
        return render(request, 'PlanIlan/home.html', context)
    elif request.method == 'POST':
        if request.POST.get('PostID', ''):
            teacher_post = TeacherReview.objects.get(id=request.POST.get('PostID', ''))
            teacher_post.amount_of_likes += int(request.POST.get('to_add', ''))
            teacher_post.save()
            return render(request, 'PlanIlan/home.html', context)
        elif request.POST.get('Rating_course_ID', ''):
            print(request.POST.get('rate_number'))
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
        courses_list = Lesson.objects.all()
        course_filter = CourseInstanceFilter(request.GET, queryset=courses_list)
        courses_list = course_filter.qs
        context = {'course_filter': course_filter, 'courses': courses_list}
        if request.is_ajax():
            json_course_list = serializers.serialize("json", courses_list)
            json_course_names = [lesson.name for lesson in courses_list]
            context = {'json_course_list': json_course_list, 'json_course_names': json_course_names}
            return JsonResponse(context, safe=False)
        return render(request, 'PlanIlan/timetable.html', context)
    return render(request, 'PlanIlan/timetable.html')

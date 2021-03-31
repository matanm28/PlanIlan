from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .decorators import unauthenticated_user, authenticated_user
from .filters import CourseInstanceFilter
from .forms import CreateUserForm
from .models import *


# @login_required(login_url='')


def search(request):
    if request.method == 'GET':
        # COURSE SEARCH ENGINE
        courses = CourseInstance.objects.all()
        course_filter = CourseInstanceFilter(request.GET, queryset=courses)
        courses = course_filter.qs
        context = {'course_filter': course_filter, 'courses': courses}
        return render(request, 'PlanIlan/search.html', context)
    return render(request, 'PlanIlan/search.html')


def home(request):
    # todo: get last teachers and courses
    # todo: save them in data structure
    # TEACHER BEST RATINGS VIEW
    teachers_obj = [Teacher.objects.get(name="ארז שיינר"),
                    Teacher.objects.get(name="גל קמינקא")]
    # COURSES BEST RATING VIEW
    courses_obj = [CourseInstance.objects.get(course__name="מערכות בריאות בארץ ובעולם"),
                   CourseInstance.objects.get(course__name="מבוא למדעי החיים")]
    # LATEST COMMENTS
    teacher_comments = TeacherPost.objects.all().order_by('date')
    context = {'teachers': teachers_obj, 'courses_obj': courses_obj,
               'teacher_comments': teacher_comments}
    if request.method == 'GET':
        return render(request, 'PlanIlan/home.html', context)
    elif request.method == 'POST':
        if request.POST.get('PostID', ''):
            teacher_post = TeacherPost.objects.get(id=request.POST.get('PostID', ''))
            teacher_post.amount_of_likes += int(request.POST.get('to_add', ''))
            teacher_post.save()
            return render(request, 'PlanIlan/home.html', context)
        elif request.POST.get('Rating_course_ID', ''):
            print(request.POST.get('rate_number'))
            course_id = CourseInstance.objects.get(id=request.POST.get('Rating_course_ID', ''))
            course_id.course.rating.update_rating(int(request.POST.get('rate_number', '')))
    return render(request, 'PlanIlan/home.html')


@unauthenticated_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            faculty = request.POST.get('faculty')
            user = form.save()
            UserModel.objects.create(
                user=user,
                user_name=user.username,
                email=user.email,
                faculty=faculty
            )
            # messages.success(request, 'ההרשמה נקלטה בהצלחה')
            login(request, user)
            return redirect('home')
    context = {'form': form}
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
    return render(request, 'PlanIlan/timetable.html')


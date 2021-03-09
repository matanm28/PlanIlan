from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .decorators import unauthenticated_user
from .models import *
from .filters import CourseFilter
# @login_required(login_url='')
from django.contrib.auth.decorators import login_required

from .forms import CreateUserForm


def home(request):
    # todo: get last teachers and courses
    # todo: save them in data structure
    if request.method == 'GET':
        # COURSE SEARCH ENGINE
        courses = Course.objects.all()
        course_filter = CourseFilter(request.GET, queryset=courses)
        courses = course_filter.qs
        # TEACHER BEST RATINGS VIEW
        teachers_obj = [Teacher.objects.get(name="ארז שיינר"), Teacher.objects.get(name="גל קמינקא")]
        # COURSES BEST RATING VIEW
        courses_obj = [Course.objects.get(code="75122"), Course.objects.get(code="99929")]
        context = {'teachers': teachers_obj, 'course_filter': course_filter, 'courses': courses,
                   'courses_obj': courses_obj}
        return render(request, 'PlanIlan/home.html', context)
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

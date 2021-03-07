from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .decorators import unauthenticated_user
from .models import *
# @login_required(login_url='')
# @allowed_user(allowed_roles=[''])
from django.contrib.auth.decorators import login_required

from .forms import CreateUserForm


def home(request):
    #todo: get last teachers and courses
    #todo: save them in data structure
    if request.method == 'GET':
        teachers_obj = [Teacher.objects.get(name="ארז שיינר"), Teacher.objects.get(name="גל קמינקא")]
        context = {'teachers': teachers_obj}
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
            messages.success(request, 'ההרשמה נקלטה בהצלחה')
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

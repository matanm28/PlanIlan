from django.shortcuts import render

from PlanIlan.models import *


def home(request):
    return render(request, 'PlanIlanApp/home.html')


def login(request):
    if request.method == 'POST':
        if 'login' in request.POST.values():
            username = request.POST.get('username')
            u = User.get_user_by_user_name(username)
            if u is not None:
                context = {'username': username}
                return render(request, 'PlanIlanApp/home.html', context)
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            u = User.create(user_name=username, email=email, password=password)
            u.save()
            context = {'username': username}
            return render(request, 'PlanIlanApp/home.html', context)
    else:
        return render(request, 'PlanIlanApp/login.html')

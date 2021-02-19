from django.shortcuts import render

from PlanIlan.models import *


def home(request):
    return render(request, 'PlanIlanApp/home.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        u = User.create(user_name=username, email=email, password=password)
        u.save()
        return render(request, 'PlanIlanApp/home.html')
    else:
        return render(request, 'PlanIlanApp/login.html')

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions

# Create your views here.
from plan_ilan.apps.api.serializers import CourseSerializer
from plan_ilan.apps.web_site.models import Course


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    

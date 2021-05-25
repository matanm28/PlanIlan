from plan_ilan.apps.web_site.models import *
from rest_framework import serializers


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ['code', 'name']

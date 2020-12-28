from rest_framework.serializers import ModelSerializer

from PlanIlan.models import Course


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['id']

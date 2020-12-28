from rest_framework.serializers import ModelSerializer

from PlanIlan.models import LessonTime


class LessonTimeSerializer(ModelSerializer):
    class Meta:
        model = LessonTime
        fields = '__all__'
        read_only_fields = ['id']

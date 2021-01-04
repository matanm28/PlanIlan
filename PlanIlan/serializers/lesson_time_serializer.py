from rest_framework.serializers import ModelSerializer

from PlanIlan.models import SessionTime


class LessonTimeSerializer(ModelSerializer):
    class Meta:
        model = SessionTime
        fields = '__all__'
        read_only_fields = ['id']

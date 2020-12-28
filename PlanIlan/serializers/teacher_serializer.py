from rest_framework.serializers import ModelSerializer

from PlanIlan.models import Teacher


class TeacherSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'
        read_only_fields = ['id']




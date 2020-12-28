from rest_framework.serializers import ModelSerializer

from PlanIlan.models import Rating


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['id']

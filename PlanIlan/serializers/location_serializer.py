from rest_framework.serializers import ModelSerializer

from PlanIlan.models import Location


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['id']

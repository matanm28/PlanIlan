from collections import OrderedDict
from operator import itemgetter

from rest_framework import serializers
from rest_framework.fields import empty

from plan_ilan.apps.web_site.models import Exam, Location, LessonTime


class NonNullModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Here we filter the null values and creates a new dictionary
        # We use OrderedDict like in original method
        ret = OrderedDict(filter(itemgetter(1), ret.items()))
        return ret


class EnumSerializer(serializers.Serializer):
    number = serializers.IntegerField(read_only=True)
    label = serializers.CharField(max_length=60, read_only=True)

    def __init__(self, enumModel, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.enumModel = enumModel

    def create(self, validated_data):
        enum = self.enumModel.objects.filter(**validated_data)
        if enum.count() == 0:
            raise serializers.ValidationError('not a valid enum')
        return enum.first()

    def update(self, instance, validated_data):
        raise NotImplemented("can't update EnumModels")


class ExamSerializer(serializers.HyperlinkedModelSerializer):
    period = serializers.StringRelatedField(read_only=True)
    date = serializers.DateTimeField('%d.%m.%y')
    time = serializers.DateTimeField('%H:%M', source='date')

    class Meta:
        model = Exam
        fields = ['period', 'date', 'time']


class LocationSerializer(NonNullModelSerializer):
    class Meta:
        model = Location
        fields = ['building_name', 'building_number', 'class_number', 'online']


class LessonTimeSerializer(serializers.HyperlinkedModelSerializer):
    day = serializers.StringRelatedField(read_only=True)
    semester = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = LessonTime
        fields = ['day', 'start_time', 'end_time', 'semester', 'year']

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from plan_ilan.apps.api.serializers import IntervalSerializer, TimeIntervalSerializer, TimetableSerializer, \
    TimetableCommonInfoSerializer, BlockedTimePeriodSerializer, RankedLessonSerializer

from plan_ilan.apps.timetable_generator.models import *
from plan_ilan.utils.general import name_of


class TimeIntervalViewSet(viewsets.ModelViewSet):
    queryset = TimeInterval.objects.all()
    serializer_class = TimeIntervalSerializer


class IntervalViewSet(viewsets.ModelViewSet):
    queryset = Interval.objects.all()
    serializer_class = IntervalSerializer


class BlockedTimePeriodViewSet(viewsets.ModelViewSet):
    queryset = BlockedTimePeriod.objects.all()
    serializer_class = BlockedTimePeriodSerializer


class RankedLessonViewSet(viewsets.ModelViewSet):
    queryset = RankedLesson.objects.all()
    serializer_class = RankedLessonSerializer


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

from rest_framework import serializers

from plan_ilan.apps.timetable_generator.models import TimeInterval, Interval, RankedLesson
from plan_ilan.apps.timetable_generator.models.timetable import TimetableCommonInfo, BlockedTimePeriod, Timetable
from . import course_serializers
from ...web_site.models import Lesson, DepartmentEnum


class TimeIntervalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeInterval
        fields = ['start', 'end']


class BlockedTimePeriodSerializer(serializers.ModelSerializer):
    day = serializers.StringRelatedField()
    blocked_time_periods = TimeIntervalSerializer(many=True)

    class Meta:
        model = BlockedTimePeriod
        fields = ['day', 'blocked_time_periods']


class IntervalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interval
        fields = ['left', 'right']


class RankedLessonSerializer(serializers.ModelSerializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.filter(course__department__number=DepartmentEnum.COMPUTER_SCIENCE).all())

    class Meta:
        model = RankedLesson
        fields = ['lesson', 'rank']


class TimetableCommonInfoSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='account__username')

    class Meta:
        model = TimetableCommonInfo
        fields = ['account', 'username', 'name']


class TimetableSerializer(serializers.ModelSerializer):
    common_info = TimetableCommonInfo()
    mandatory_lessons = RankedLessonSerializer(many=True)
    elective_lessons = RankedLessonSerializer(many=True)
    blocked_time_periods = BlockedTimePeriodSerializer(many=True)
    elective_points_bound = IntervalSerializer()
    semester = serializers.StringRelatedField()

    class Meta:
        model = Timetable
        fields = ['common_info', 'mandatory_lessons', 'elective_lessons', 'blocked_time_periods', 'elective_points_bound',
                  'semester', 'max_num_of_days', 'created', 'modified']

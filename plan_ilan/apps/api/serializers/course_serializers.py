from rest_framework import serializers

from .general_serializers import ExamSerializer, LocationSerializer, LessonTimeSerializer
from .teacher_serializers import TeacherBasicSerializer
from plan_ilan.apps.web_site.models import Course, Lesson


class CourseBasicSerializer(serializers.ModelSerializer):
    faculty = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Course
        fields = ['code', 'name', 'faculty']


class CourseExtendedSerializer(CourseBasicSerializer):
    department = serializers.StringRelatedField(read_only=True)
    points = serializers.FloatField(source='total_points', read_only=True)
    exams = ExamSerializer(many=True, read_only=True)

    class Meta(CourseBasicSerializer.Meta):
        fields = CourseBasicSerializer.Meta.fields + ['department', 'points', 'exams', 'syllabus_link']


class CourseExtraDetailsSerializer(CourseExtendedSerializer):
    lessons = serializers.HyperlinkedRelatedField(view_name='lesson-detail', read_only=True, many=True)

    class Meta(CourseExtendedSerializer.Meta):
        fields = CourseExtendedSerializer.Meta.fields + ['lessons']


class LessonBasicSerializer(serializers.HyperlinkedModelSerializer):
    lesson_type = serializers.StringRelatedField()

    class Meta:
        model = Lesson
        fields = ['pk', 'group', 'lesson_type']


class LessonExtendedSerializer(LessonBasicSerializer):
    locations = LocationSerializer(many=True)
    session_times = LessonTimeSerializer(many=True)

    class Meta(LessonBasicSerializer.Meta):
        fields = list(set(LessonBasicSerializer.Meta.fields).symmetric_difference(
            ['pk', 'locations', 'session_times', 'points', 'details_link']))


class LessonFullDetailsSerializer(LessonExtendedSerializer):
    teachers = TeacherBasicSerializer(many=True)

    class Meta(LessonExtendedSerializer.Meta):
        fields = LessonExtendedSerializer.Meta.fields + ['teachers']


class CourseFullDetailsSerializer(CourseExtendedSerializer):
    lessons = LessonExtendedSerializer(read_only=True, many=True)

    class Meta(CourseExtendedSerializer.Meta):
        fields = CourseExtendedSerializer.Meta.fields + ['lessons']

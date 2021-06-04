from plan_ilan.apps.api import serializers as api_serializers


class CourseSearchSerializer(api_serializers.CourseFullDetailsSerializer):
    lessons = api_serializers.LessonFullDetailsSerializer(many=True)

    class Meta(api_serializers.CourseFullDetailsSerializer.Meta):
        pass

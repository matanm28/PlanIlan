from plan_ilan.apps.api import serializers as api_serializers


class TeacherSearchSerializer(api_serializers.TeacherExtendedSerializer):
    courses = api_serializers.CourseBasicSerializer(many=True)

    class Meta(api_serializers.TeacherExtendedSerializer.Meta):
        fields = api_serializers.TeacherExtendedSerializer.Meta.fields + ['courses']

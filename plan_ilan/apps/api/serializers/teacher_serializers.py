from rest_framework import serializers

from plan_ilan.apps.api.serializers.general_serializers import NonNullModelSerializer
from plan_ilan.apps.web_site.models import Teacher


class TeacherBasicSerializer(NonNullModelSerializer):
    title = serializers.StringRelatedField()

    class Meta:
        model = Teacher
        fields = ['pk', 'title', 'name']


class TeacherExtendedSerializer(TeacherBasicSerializer):
    faculty = serializers.StringRelatedField()
    departments = serializers.StringRelatedField(many=True)

    class Meta(TeacherBasicSerializer.Meta):
        fields = TeacherBasicSerializer.Meta.fields + ['faculty', 'departments', 'phone', 'email', 'office',
                                                       'website_url', 'image']


class TeacherFullDetailsSerializer(TeacherExtendedSerializer):
    courses = serializers.HyperlinkedRelatedField(view_name='course-detail', many=True,
                                                  read_only=True)

    class Meta(TeacherExtendedSerializer.Meta):
        fields = TeacherExtendedSerializer.Meta.fields + ['courses']

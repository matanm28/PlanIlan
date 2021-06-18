from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from plan_ilan.apps.api.serializers import LessonBasicSerializer, LessonFullDetailsSerializer, \
    LessonTimeSerializer, CourseBasicSerializer, CourseExtendedSerializer, CourseExtraDetailsSerializer, \
    CourseFullDetailsSerializer, LocationSerializer, TeacherBasicSerializer, TeacherExtendedSerializer, \
    TeacherFullDetailsSerializer, ExamSerializer
from plan_ilan.apps.web_site.models import *


class BaseListAndRetrieveViewSet(viewsets.ReadOnlyModelViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert hasattr(self, 'list_serializer_class')
        assert hasattr(self, 'detail_serializer_class')
        self.serializer_class = self.list_serializer_class

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = self.detail_serializer_class
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.serializer_class = self.list_serializer_class
        return super().list(request, *args, **kwargs)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['faculty', 'department']
    search_fields = ['name', 'code', 'faculty__label', 'department__label']

    @action(detail=True, methods=['get'], name='Course Lessons')
    def lessons(self, request, pk: str = None):
        course_object = self.get_object()
        course_serializer = CourseExtendedSerializer(course_object)
        lesson_serializer = LessonFullDetailsSerializer(course_object.lessons, context={'request': request}, many=True)
        return Response({**course_serializer.data, 'lessons': lesson_serializer.data})

    @action(detail=True, methods=['get'], name='Course Teachers')
    def teachers(self, request, pk: str = None):
        course_object = self.get_object()
        course_serializer = CourseExtendedSerializer(course_object)
        teachers_queryset = Teacher.objects.filter(lessons__course=course_object).distinct().order_by('title', 'name')
        teacher_serializer = TeacherExtendedSerializer(teachers_queryset, context={'request': request}, many=True)
        return Response({**course_serializer.data, 'teachers': teacher_serializer.data})

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseExtraDetailsSerializer
        else:
            return CourseBasicSerializer


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Teacher.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['faculty', 'title']
    search_fields = ['name', 'title__label', 'faculty__label']

    @action(detail=True, methods=['get'], name='Teacher Courses')
    def courses(self, request, pk: str = None):
        teacher_object = self.get_object()
        context = {'request': request}
        teacher_serializer = TeacherBasicSerializer(teacher_object)
        course_serializer = CourseFullDetailsSerializer(teacher_object.courses, context=context, many=True)
        return Response({**teacher_serializer.data, 'courses': course_serializer.data})

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeacherFullDetailsSerializer
        else:
            return TeacherBasicSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['building_name', 'building_number', 'class_number', 'online']


class LessonTimeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LessonTime.objects.all()
    serializer_class = LessonTimeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['day', 'semester', 'start_time', 'end_time', 'year']


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lesson_type', 'points']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonFullDetailsSerializer
        else:
            return LessonBasicSerializer

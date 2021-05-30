from collections import OrderedDict, defaultdict
from typing import List, Type

from rest_framework import permissions, viewsets, views, filters
from rest_framework.response import Response
from rest_framework.reverse import NoReverseMatch, reverse
from rest_framework.decorators import action, api_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from plan_ilan.apps.api.serializers import *
from plan_ilan.apps.web_site.models import *
from ...exceptaions import ModelNotFoundError
from ...utils.general import name_of


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


def right_replace(string: str, old: str, new: str, count: int = 1):
    return f'{new}'.join(string.rsplit(f'{old}', maxsplit=count))


def flatten_dict(dd, separator='-', prefix=''):
    return {prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
            } if isinstance(dd, dict) else {prefix: dd}


class PlanIlanRootView(APIView):
    """
    This page shows all the API endpoints we are currently providing.\n
    Mind that the API endpoints that has a "list" prefix returns paginated results.\n
    Play around and take a look yourselves :)
    """
    permission_classes = [permissions.AllowAny]

    @classmethod
    def as_view(cls, registered_view_sets: List[Type], **initkwargs):
        cls.registered_view_sets = registered_view_sets
        return super().as_view(**initkwargs)

    def get(self, request):
        api_root_data = {}
        for view_set in self.registered_view_sets:
            model_class = view_set.queryset.model
            model_name = model_class._meta.verbose_name.replace(' ', '')
            model_name_plural = model_class._meta.verbose_name_plural
            try:
                sample_object_pk = model_class.objects.first().pk
            except (AttributeError, Exception):
                raise ModelNotFoundError(model_class, "Can't generate api-root view")
            details_url = right_replace(reverse(f'{model_name}-detail', args=[sample_object_pk], request=request),
                                        sample_object_pk, f'<{name_of(type(sample_object_pk))}:pk>')
            api_root_data[model_name_plural] = {
                'list': reverse(f'{model_name}-list', request=request),
                'details': details_url
            }
            for extra_action in view_set.get_extra_actions():
                args = [sample_object_pk] if extra_action.detail else []
                view_name = f'{model_name}-{extra_action.url_path}'
                resolved_url = reverse(view_name, args=args, request=request)
                if extra_action.detail:
                    resolved_url = right_replace(resolved_url, sample_object_pk,
                                                 f'<{name_of(type(sample_object_pk))}:pk>')
                api_root_data[model_name_plural][extra_action.url_name] = resolved_url
        return Response(flatten_dict(api_root_data))

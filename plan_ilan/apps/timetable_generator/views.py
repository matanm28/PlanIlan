from abc import abstractmethod
from typing import Dict, Iterable

from django.http import HttpResponseBadRequest, QueryDict, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from plan_ilan.apps.web_site.decorators import authenticated_user
from plan_ilan.apps.web_site.models import Lesson, Course, Account, Department, SemesterEnum
from .forms import FirstForm, DepartmentsForm
from .models import RankedLesson, Timetable


def reverse_querystring(view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None):
    '''
    Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'})
    origin: https://gist.github.com/benbacardi/227f924ec1d9bedd242b
    '''
    base_url = reverse(view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    if query_kwargs:
        query_dict = QueryDict(mutable=True)
        for key, item in query_kwargs.items():
            if not isinstance(item, Iterable):
                query_dict.update({key: item})
                break
            for value in item:
                query_dict.appendlist(key, value)
        return f'{base_url}?{query_dict.urlencode()}'
    return base_url


class AuthenticatedUserTemplateView(TemplateView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = self.get_context()
        return {**super().get_context_data(**kwargs), **context}

    @abstractmethod
    def get_context(self) -> Dict:
        pass

    def post(self, request, *args, **kwargs):
        pass


class QueryStringHandlingTemplateView(AuthenticatedUserTemplateView):
    view_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.view_name is not None, f'got {self.view_name=} - must be defined'

    def get(self, request, *args, **kwargs):
        if self.request.META['QUERY_STRING']:
            self.request.session['data'] = self.request.GET.urlencode()
            return HttpResponseRedirect(reverse(self.view_name))
        return super().get(request, *args, **kwargs)

    @abstractmethod
    def get_context(self) -> Dict:
        pass




class FirstView(AuthenticatedUserTemplateView):
    template_name = 'timetable_generator/first_form.html'

    def get_context(self):
        return {'form': FirstForm()}

    def post(self, request, *args, **kwargs):
        form = FirstForm(self.request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest(form.errors.as_data())
        account = get_object_or_404(Account, user=self.request.user)
        timetable = Timetable.temporal_create(account=account, **form.cleaned_data)
        self.request.session['timetable_pk'] = timetable.pk
        return redirect('pick-deps')


class PickDepartmentsView(AuthenticatedUserTemplateView):
    template_name = 'timetable_generator/pick_deps.html'

    def post(self, request, *args, **kwargs):
        mandatory = DepartmentsForm(data=self.request.POST, prefix='mandatory')
        elective = DepartmentsForm(data=self.request.POST, prefix='elective')
        if not mandatory.is_valid():
            return HttpResponseBadRequest(mandatory.errors.as_data())
        if not elective.is_valid():
            return HttpResponseBadRequest(elective.errors.as_data())
        query_dict = {
            'mandatory': mandatory.cleaned_data.get('departments', Department.objects.none()).values_list('number',
                                                                                                          flat=True),
            'elective': elective.cleaned_data.get('departments', Department.objects.none()).values_list('number',
                                                                                                        flat=True),
        }
        return redirect(reverse_querystring('pick-courses', query_kwargs=query_dict))

    def get_context(self, **kwargs) -> Dict:
        return {
            'mandatory_form': DepartmentsForm(prefix='mandatory'),
            'elective_form': DepartmentsForm(prefix='elective')
        }


class PickCoursesView(QueryStringHandlingTemplateView):
    template_name = 'timetable_generator/pick_courses.html'
    view_name = 'pick-courses'

    def get_context(self):
        query_dict = QueryDict(self.request.session.get('data', None))
        if not query_dict:
            pass
        timetable = get_object_or_404(Timetable, pk=self.request.session.get('timetable_pk', None))
        valid_semesters = [timetable.semester]
        if timetable.semester in [SemesterEnum.FIRST, SemesterEnum.SECOND]:
            valid_semesters.append(SemesterEnum.YEARLY)
        course_mandatory = (Course.objects
                            .filter(department__in=query_dict.getlist('mandatory', []),
                                    lessons__session_times__semester__in=valid_semesters)
                            .distinct()
                            .order_by('department', 'name'))
        course_elective = (Course.objects
                           .filter(department__in=query_dict.getlist('elective', []),
                                   lessons__session_times__semester__in=valid_semesters)
                           .distinct()
                           .order_by('department', 'name'))
        return {"course_elective": course_elective, "course_mandatory": course_mandatory}

    def post(self, request, *args, **kwargs):
        mandatory_courses = request.POST.getlist('mandatory')
        elective_courses = request.POST.getlist('elective')
        course_dict = {
            'mandatory': Course.objects.filter(code__in=mandatory_courses).values_list('code', flat=True),
            'elective': Course.objects.filter(code__in=elective_courses).values_list('code', flat=True),
        }
        return redirect(reverse_querystring('pick-lessons', query_kwargs=course_dict))


class PickLessonsView(QueryStringHandlingTemplateView):
    template_name = 'timetable_generator/pick_lessons.html'
    view_name = 'pick-lessons'

    def get_context(self):
        query_dict = QueryDict(self.request.session.get('data', None))
        if not query_dict:
            pass
        mandatory_courses = Course.objects.filter(code__in=query_dict.getlist('elective', []))
        elective_courses = Course.objects.filter(code__in=query_dict.getlist('mandatory', []))
        return {"mandatory_courses": mandatory_courses, "elective_courses": elective_courses}

    def post(self, request, *args, **kwargs):
        mandatory_lessons = request.POST.getlist('mandatory-lessons')
        elective_lessons = request.POST.getlist('elective-lessons')
        lesson_dict = {
            'mandatory': Lesson.objects.filter(pk__in=mandatory_lessons).values_list('pk', flat=True),
            'elective': Lesson.objects.filter(pk__in=elective_lessons).values_list('pk', flat=True),
        }
        return redirect(reverse_querystring('build-timetable', query_kwargs=lesson_dict))


class BuildTimeTableView(QueryStringHandlingTemplateView):
    template_name = 'timetable_generator/build_timetable.html'
    view_name = 'build-timetable'

    def get_context(self):
        query_dict = QueryDict(self.request.session.get('data', None))
        mandatory_lessons = Lesson.objects.filter(pk__in=query_dict.getlist('elective', []))
        elective_lessons = Lesson.objects.filter(pk__in=query_dict.getlist('mandatory', []))
        timetable = get_object_or_404(Timetable, pk=self.request.session.get('timetable_pk', None))
        return {"mandatory_lessons": mandatory_lessons, "elective_lessons": elective_lessons}


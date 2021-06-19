import json
from abc import abstractmethod
from typing import Dict, List, Tuple, Iterable

from django.db.models import QuerySet
from django.http import HttpResponseBadRequest, QueryDict, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils.http import urlencode

from plan_ilan.apps.web_site.decorators import authenticated_user
from plan_ilan.apps.web_site.models import Lesson, Course, Account, Department, Semester, SemesterEnum
from .models import RankedLesson, Timetable
from .forms import FirstForm, DepartmentsForm


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
        timetable = get_object_or_404(Timetable, pk=self.request.session.get('timetable_pk', None))
        mandatory = DepartmentsForm(data=self.request.POST, prefix='mandatory')
        elective = DepartmentsForm(data=self.request.POST, prefix='elective')
        if not mandatory.is_valid():
            return HttpResponseBadRequest(mandatory.errors.as_data())
        if not elective.is_valid():
            return HttpResponseBadRequest(elective.errors.as_data())
        query_dict = {
            'mandatory': mandatory.cleaned_data.get('departments', Department.objects.none()).values_list('number', flat=True),
            'elective': elective.cleaned_data.get('departments', Department.objects.none()).values_list('number', flat=True),
        }
        return redirect(reverse_querystring('pick-courses', query_kwargs=query_dict))

    def get_context(self, **kwargs) -> Dict:
        return {
            'mandatory_form': DepartmentsForm(prefix='mandatory'),
            'elective_form': DepartmentsForm(prefix='elective')
        }


@authenticated_user
def pick_courses(request):
    if request.META['QUERY_STRING']:
        request.session['data'] = request.GET.urlencode()
        return HttpResponseRedirect(reverse('pick-courses'))
    query_dict = QueryDict(request.session.get('data', None))
    if not query_dict:
        pass
    timetable = get_object_or_404(Timetable, pk=request.session.get('timetable_pk', None))
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
    context = {"course_elective": course_elective, "course_mandatory": course_mandatory}
    return render(request, 'timetable_generator/pick_courses.html', context)


@authenticated_user
def pick_lessons(request):
    mand_courses = request.POST.getlist("mand")
    mand_list = Course.objects.filter(pk__in=mand_courses)
    elect_courses = request.POST.getlist("elect")
    elect_list = Course.objects.filter(pk__in=elect_courses)
    context = {"mand_list": mand_list, "elect_list": elect_list}
    return render(request, 'timetable_generator/pick_lessons.html', context)


@authenticated_user
def build_timetable(request):
    selected_mand_lessons = request.POST.getlist("mand-lessons")
    ranks_mand = request.POST.getlist("rank-mand-lesson")
    mand_lessons = Lesson.objects.select_related("course").filter(pk__in=selected_mand_lessons)
    selected_elect_lessons = request.POST.getlist("elect-lessons")
    ranks_elect = request.POST.getlist("rank-elect-lesson")
    elect_lessons = Lesson.objects.select_related("course").filter(pk__in=selected_elect_lessons)
    ranked_mand = [RankedLesson.create(lesson, rank) for (lesson, rank) in zip(mand_lessons, ranks_mand)]
    ranked_elect = [RankedLesson.create(lesson, rank) for (lesson, rank) in zip(elect_lessons, ranks_elect)]
    return render(request, 'timetable_generator/build_timetable.html')

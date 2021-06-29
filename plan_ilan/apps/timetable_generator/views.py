from abc import abstractmethod
from typing import Dict, Iterable

from django.contrib import messages
from django.http import HttpResponseBadRequest, QueryDict, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from plan_ilan.apps.web_site.models import Lesson, Course, Account, Department
from .forms import FirstForm, DepartmentsForm, BlockedTimesFormSet
from .models import RankedLesson, Timetable, Interval, TimeInterval


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
            self.request.session[f'data_{self.view_name}'] = self.request.GET.urlencode()
            return HttpResponseRedirect(reverse(self.view_name))
        return super().get(request, *args, **kwargs)

    @abstractmethod
    def get_context(self) -> Dict:
        pass


class FirstView(AuthenticatedUserTemplateView):
    template_name = 'timetable_generator/first_form.html'

    def get_context(self):
        data = None
        if 'timetable_pk' in self.request.session:
            timetable = get_object_or_404(Timetable, pk=self.request.session['timetable_pk'])
            data = {
                'name': timetable.name,
                'semester': timetable.semester,
                'max_num_of_days': timetable.max_num_of_days
            }
        blocked_times_formset = BlockedTimesFormSet()
        return {'form': FirstForm(initial=data), 'is_rerun': True, 'blocked_times_formset': blocked_times_formset}

    def post(self, request, *args, **kwargs):
        blocked_times_formset = BlockedTimesFormSet(self.request.POST)
        form = FirstForm(self.request.POST)
        if not form.is_valid() or not blocked_times_formset.is_valid():
            return HttpResponseBadRequest(form.errors.as_data())
        blocked_times_dict = {}
        for block in blocked_times_formset.cleaned_data:
            time_interval = TimeInterval.create(block['start'], block['end'])
            if block['day'] in blocked_times_dict:
                blocked_times_dict[block['day']].append(time_interval)
            else:
                blocked_times_dict[block['day']] = [time_interval]
        blocked_times = list(blocked_times_dict.items())
        account = get_object_or_404(Account, user=self.request.user)
        timetable = Timetable.create(account=account, **form.cleaned_data, blocked_time_periods=blocked_times,
                                     elective_lessons=[], mandatory_lessons=[], elective_points_bound=None)
        self.request.session['timetable_pk'] = timetable.pk
        return redirect('pick-deps')


class PickDepartmentsView(AuthenticatedUserTemplateView):
    template_name = 'timetable_generator/pick_deps.html'

    def post(self, request, *args, **kwargs):
        mandatory = DepartmentsForm(data=self.request.POST, prefix='mandatory')
        elective = DepartmentsForm(accept_empty=True, data=self.request.POST, prefix='elective')
        if not mandatory.is_valid():
            messages.info(request, 'יש לבחור לפחות מחלקת חובה אחת')
            return redirect('pick-deps')
            # return HttpResponseBadRequest("test")
        elective.full_clean()
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
        query_dict = QueryDict(self.request.session.get(f'data_{self.view_name}', None))
        if not query_dict:
            pass
        timetable = get_object_or_404(Timetable, pk=self.request.session.get('timetable_pk', None))
        valid_semesters = timetable.valid_semesters
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
        points_bound = request.POST.getlist('elective_points', ['0,0'])[0].split(",")
        left_bound, right_bound = [int(points) for points in points_bound]
        timetable = get_object_or_404(Timetable, pk=self.request.session.get('timetable_pk', None))
        timetable.elective_points_bound = Interval.create(left_bound, right_bound)
        timetable.save()
        mandatory_courses = request.POST.getlist('mandatory', [])
        elective_courses = request.POST.getlist('elective', [])
        # query_dict = QueryDict(self.request.session.get(f'data_{self.view_name}', None))
        # elective_deps = query_dict.getlist('elective', [])
        # if not mandatory_courses or (not elective_courses and elective_deps):
        #     messages.info(request, 'יש לבחור לפחות קורס חובה/בחירה אחד')
        #     return redirect('pick-courses')
        course_dict = {
            'mandatory': Course.objects.filter(code__in=mandatory_courses).values_list('code', flat=True),
            'elective': Course.objects.filter(code__in=elective_courses).values_list('code', flat=True),
        }
        return redirect(reverse_querystring('pick-lessons', query_kwargs=course_dict))


class PickLessonsView(QueryStringHandlingTemplateView):
    template_name = 'timetable_generator/pick_lessons.html'
    view_name = 'pick-lessons'

    def get_context(self):
        query_dict = QueryDict(self.request.session.get(f'data_{self.view_name}', None))
        if not query_dict:
            pass
        mandatory_courses = Course.objects.filter(code__in=query_dict.getlist('mandatory', []))
        elective_courses = Course.objects.filter(code__in=query_dict.getlist('elective', []))
        return {"mandatory_courses": mandatory_courses, "elective_courses": elective_courses}

    def post(self, request, *args, **kwargs):
        mandatory_lessons = request.POST.getlist('mandatory-lessons', [])
        elective_lessons = request.POST.getlist('elective-lessons', [])
        mandatory_ranks = request.POST.getlist('rank-mandatory-lesson', [])
        elective_ranks = request.POST.getlist('rank-elective-lesson', [])
        lesson_dict = {
            'mandatory_lessons': Lesson.objects.filter(pk__in=mandatory_lessons).values_list('pk', flat=True),
            'elective_lessons': Lesson.objects.filter(pk__in=elective_lessons).values_list('pk', flat=True),
            'mandatory_ranks': mandatory_ranks,
            'elective_ranks': elective_ranks,
        }
        return redirect(reverse_querystring('build-timetable', query_kwargs=lesson_dict))


class BuildTimeTableView(QueryStringHandlingTemplateView):
    template_name = 'timetable_generator/build_timetable.html'
    view_name = 'build-timetable'

    def get_context(self):
        query_dict = QueryDict(self.request.session.get(f'data_{self.view_name}', None))
        if query_dict.get('ready_timetable', None):
            timetable = Timetable.objects.get(pk=query_dict.get('ready_timetable', None))
        else:
            mandatory_lessons = Lesson.objects.filter(pk__in=query_dict.getlist('mandatory_lessons', []))
            elective_lessons = Lesson.objects.filter(pk__in=query_dict.getlist('elective_lessons', []))
            mandatory_ranks = query_dict.getlist('mandatory_ranks', [])
            elective_ranks = query_dict.getlist('elective_ranks', [])
            mandatory_ranked_lessons = [RankedLesson.create(lesson, rank)
                                        for rank, lesson in zip(mandatory_ranks, mandatory_lessons)]
            elective_ranked_lessons = [RankedLesson.create(lesson, rank)
                                       for rank, lesson in zip(elective_ranks, elective_lessons)]
            timetable = get_object_or_404(Timetable, pk=self.request.session.get('timetable_pk', None))
            timetable.mandatory_lessons.set(mandatory_ranked_lessons)
            timetable.elective_lessons.set(elective_ranked_lessons)
            timetable.is_done = True
            timetable.save()
        solutions = timetable.get_solutions()
        # l = []
        # d = [s.as_dict for s in solutions.all()]
        d = [s.as_table_arr for s in solutions.all()]
        # for sol in d:
        #     dict_list = []
        #     for day in sorted(sol.keys()):
        #         lessons_list = []
        #         for hour in sorted(sol[day].keys()):
        #             lessons_list.append(hour)
        #             lessons_list.append([sol[day][hour]])
        #         dict_list.append(day)
        #         dict_list.append(lessons_list)
        #     l.append(dict_list)
        return {'solutions': solutions, 'solution_arr': d}


class LandingPageView(QueryStringHandlingTemplateView):
    template_name = 'timetable_generator/landing_page.html'
    view_name = 'landing-page'

    def get_context(self):
        account = get_object_or_404(Account, user=self.request.user)
        timetable_names = Timetable.objects.filter(common_info__account=account, is_done=True).values_list(
            'common_info__name',
            flat=True)
        return {"timetable_names": timetable_names}

    def post(self, request, *args, **kwargs):
        if 'new_timetable' in request.POST:
            return redirect('first-form')

        timetable_dict = {'ready_timetable': Timetable.objects.get(common_info__name=
                                                                   request.POST.get('old_timetable')).pk}
        return redirect(reverse_querystring('build-timetable', query_kwargs=timetable_dict))

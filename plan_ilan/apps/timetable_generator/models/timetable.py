from collections import defaultdict
from datetime import time
from typing import Union, List, Tuple

from django.db import models
from django.db.models import QuerySet, Q
from model_utils.models import TimeStampedModel

from plan_ilan.apps.timetable_generator.models import TimeInterval
from plan_ilan.apps.timetable_generator.models.ranked_lesson import RankedLesson
from plan_ilan.apps.timetable_generator.models.utils import Interval
from plan_ilan.apps.web_site.models import BaseModel, Account, Semester, Course, Lesson, Day, SemesterEnum

RankedLessonList = Union[QuerySet[RankedLesson], List[RankedLesson]]


class TimetableCommonInfo(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='timetables')
    name = models.CharField(max_length=255)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='common_info')

    @classmethod
    def create(cls, account: Account, name: str, semester: Semester) -> 'TimetableCommonInfo':
        common_info, created = cls.objects.get_or_create(account=account, name=name, semester=semester)
        cls.log_created(common_info, created)
        return common_info

    def __str__(self):
        return f'{self.name} - {self.account} ({self.semester})'

    class Meta:
        ordering = ['account', 'semester', 'name', 'pk']
        unique_together = ['account', 'name', 'semester']
        db_table = 'timetables_common_infos'


BlockedTimeTuple = Tuple[Day, List[TimeInterval]]


def get_default_elective_points_bound() -> Interval:
    interval = Interval.create(left=0, right=1000)
    return interval


class Timetable(TimeStampedModel, BaseModel):
    common_info = models.OneToOneField(TimetableCommonInfo, on_delete=models.CASCADE)
    mandatory_lessons = models.ManyToManyField(RankedLesson, related_name='timetables_mandatory')
    elective_lessons = models.ManyToManyField(RankedLesson, related_name='timetables_elective')
    blocked_time_periods = models.ManyToManyField('BlockedTimePeriod', related_name='timetables')
    elective_points_bound = models.ForeignKey(Interval, on_delete=models.CASCADE,
                                              default=get_default_elective_points_bound,
                                              related_name='timetables', null=True)
    max_num_of_days = models.PositiveSmallIntegerField(default=6)
    is_done = models.BooleanField(default=False, null=True)

    @classmethod
    def create(cls, account: Account, name: str, mandatory_lessons: RankedLessonList,
               elective_lessons: RankedLessonList, blocked_time_periods: List[BlockedTimeTuple],
               elective_points_bound: Interval, semester: Semester, max_num_of_days: int) -> 'Timetable':
        common_info = TimetableCommonInfo.create(account=account, name=name, semester=semester)
        timetable, created = cls.objects.update_or_create(common_info=common_info,
                                                          defaults={
                                                              'elective_points_bound': elective_points_bound,
                                                              'max_num_of_days': max_num_of_days
                                                          })
        cls.log_created(timetable, created)
        for day, time_intervals_list in blocked_time_periods:
            BlockedTimePeriod.create(day, time_intervals_list, timetable)
        timetable.mandatory_lessons.set(mandatory_lessons)
        timetable.elective_lessons.set(elective_lessons)
        timetable.save()
        return timetable

    def __str__(self):
        return f'{self.common_info}'

    def get_solutions(self, only_solved=True) -> QuerySet['TimetableSolution']:
        from plan_ilan.apps.timetable_generator.timetable_optimizer.optimizer import TimetableOptimizer
        if not self.solutions.exists():
            optimizer = TimetableOptimizer(self)
            optimizer_solutions = optimizer.solve()
            timetable_solutions = []
            for lessons_codes_and_groups, info in optimizer_solutions:
                lessons_query = Q()
                for code, group in map(lambda s: s.split('-'), lessons_codes_and_groups):
                    lessons_query |= Q(lesson__course__code=code, lesson__group=group)
                ranked_lessons = (RankedLesson.objects.filter((Q(timetables_mandatory=self) |
                                                               Q(timetables_elective=self)) & lessons_query))
                solution = TimetableSolution.create(self.common_info, ranked_lessons, **info)
                timetable_solutions.append(solution)
        if only_solved:
            solutions = self.solutions.filter(is_solved=True)
        else:
            solutions = self.solutions
        return solutions.order_by('-score')

    class Meta:
        ordering = ['common_info', 'created']
        db_table = 'timetables'

    @property
    def courses(self) -> QuerySet[Course]:
        return self.mandatory_courses.union(self.elective_courses)

    @property
    def all_ranked_lessons(self) -> QuerySet[RankedLesson]:
        return self.mandatory_lessons.union(self.elective_lessons.all())

    @classmethod
    def __courses_from_ranked_lessons(cls, ranked_lessons: QuerySet[RankedLesson]):
        lessons_ids = list(ranked_lessons.values_list('lesson', flat=True))
        return Course.objects.filter(lessons__in=lessons_ids).distinct()

    @property
    def mandatory_courses(self) -> QuerySet[Course]:
        return self.__courses_from_ranked_lessons(self.mandatory_lessons)

    @property
    def elective_courses(self) -> QuerySet[Course]:
        return self.__courses_from_ranked_lessons(self.elective_lessons)

    @property
    def solutions(self):
        return self.common_info.solutions

    @property
    def account(self):
        return self.common_info.account

    @property
    def name(self):
        return self.common_info.name

    @property
    def blocked_days(self) -> QuerySet[Day]:
        return self.blocked_time_periods.values_list('day').distinct()

    @property
    def semester(self):
        return self.common_info.semester

    @property
    def valid_semesters(self) -> List[SemesterEnum]:
        valid_semesters = [self.semester]
        if self.semester in [SemesterEnum.FIRST, SemesterEnum.SECOND]:
            valid_semesters.append(SemesterEnum.YEARLY)
        return valid_semesters


class TimetableSolution(TimeStampedModel, BaseModel):
    common_info = models.ForeignKey(TimetableCommonInfo, on_delete=models.CASCADE, related_name='solutions')
    lessons = models.ManyToManyField(Lesson, related_name='timetable_solutions')
    score = models.FloatField(editable=False)
    iterations = models.IntegerField(editable=False)
    is_solved = models.BooleanField(editable=False)
    possibly_invalid = models.BooleanField(editable=False, default=False)

    def __str__(self):
        score = f'({self.score})' if self.is_solved else ''
        possibly_invalid_warning = f'- Might be incorrect!' if self.possibly_invalid else ''
        return f'{self.common_info} {score} {possibly_invalid_warning}'.strip()

    @classmethod
    def create(cls, common_info: TimetableCommonInfo, ranked_lessons: QuerySet[RankedLesson], iterations: int,
               is_solved: bool, objective_score: float, possibly_invalid: bool) -> 'TimetableSolution':
        solution, created = cls.objects.get_or_create(common_info=common_info, score=round(objective_score, 3),
                                                      iterations=iterations,
                                                      defaults={'is_solved': is_solved,
                                                                'possibly_invalid': possibly_invalid})
        solution.lessons.set(ranked_lessons.values_list('lesson', flat=True))
        cls.log_created(solution, created)
        return solution

    @property
    def account(self):
        return self.common_info.account

    @property
    def name(self):
        return self.common_info.name

    @property
    def semester(self):
        return self.common_info.semester

    @property
    def display_name(self):
        return f'{self.name} ({self.score})'

    @property
    def as_dict(self):
        ret = defaultdict(lambda: defaultdict(dict))
        for lesson in self.lessons.all():
            for lesson_time in lesson.session_times.all().order_by('start_time'):
                ret[lesson_time.day][lesson_time.time_str()] = lesson
        return ret

    @property
    def as_table_arr(self):
        colors = (
            '#E3E3FF', '#DFF2FD', '#E2FCE6', '#FCFADE', '#FFEEE2', '#FFDBDB', '#66BBC9', '#B4CFB1', '#F7F4EB',
            '#EAB5B9',
            '#EADEC6', '#D0EAFA', '#C5D2EF')
        times = ('08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00', '13:00-14:00',
                 '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00', '18:00-19:00', '19:00-20:00',
                 '20:00-21:00', '21:00-22:00')
        courses_colors = {}
        days = [[] for _ in range(Day.objects.count())]
        table = [[t, days.copy()] for t in times]
        for i, lesson in enumerate(self.lessons.all()):
            if lesson.course not in courses_colors.keys():
                courses_colors[lesson.course] = colors[i % (len(colors) - 1)]
            for lesson_time in lesson.session_times.all().order_by('start_time'):
                day_number = lesson_time.day.number - 1
                for hour in range(lesson_time.start_time.hour, lesson_time.end_time.hour):
                    lesson_details = [lesson, courses_colors[lesson.course]]
                    table[hour - 8][1][day_number] = lesson_details
        return table

    class Meta:
        ordering = ['-score', 'created', 'modified', 'pk']
        db_table = 'solutions'
        verbose_name = 'solution'


class BlockedTimePeriod(BaseModel):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='blocked_times')
    times = models.ManyToManyField(TimeInterval, related_name='blocked_time_periods')

    @classmethod
    def create(cls, day: Day, blocked_times: List[Union[Tuple[time, time], TimeInterval]],
               table: Timetable) -> 'BlockedTimePeriod':
        blocked_time_period, created = table.blocked_time_periods.get_or_create(day=day)
        cls.log_created(blocked_time_period, created)
        time_intervals = []
        for blocked_time in blocked_times:
            if isinstance(blocked_time, TimeInterval):
                time_intervals.append(blocked_time)
            else:
                time_interval = TimeInterval.create(*blocked_time)
                time_intervals.append(time_interval)
        blocked_time_period.times.set(time_intervals)
        return blocked_time_period

    class Meta:
        ordering = ['timetables', 'day']
        db_table = 'blocked_time_periods'

from datetime import time
from typing import Union, List, Tuple

from django.db import models
from django.db.models import QuerySet, Q
from model_utils.models import TimeStampedModel

from plan_ilan.apps.timetable_generator.models import TimeInterval
from plan_ilan.apps.timetable_generator.models.ranked_lesson import RankedLesson
from plan_ilan.apps.timetable_generator.models.utils import Interval
from plan_ilan.apps.web_site.models import BaseModel, Account, Semester, Course, Lesson, Day

RankedLessonList = Union[QuerySet[RankedLesson], List[RankedLesson]]


class TimetableCommonInfo(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='timetables')
    name = models.CharField(max_length=255)

    @classmethod
    def create(cls, account: Account, name: str) -> 'TimetableCommonInfo':
        common_info, created = cls.objects.get_or_create(account=account, name=name)
        cls.log_created(common_info, created)
        return common_info

    class Meta:
        ordering = ['account', 'name', 'pk']
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
                                              related_name='timetables')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='timetables')
    max_num_of_days = models.PositiveSmallIntegerField(default=6)

    @classmethod
    def create(cls, account: Account, name: str, mandatory_lessons: RankedLessonList,
               elective_lessons: RankedLessonList, blocked_time_periods: List[BlockedTimeTuple],
               elective_points_bound: Interval, semester: Semester, max_num_of_days: int) -> 'Timetable':
        common_info = TimetableCommonInfo.create(account=account, name=name)
        timetable, created = cls.objects.update_or_create(common_info=common_info, semester=semester,
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

    @classmethod
    def temporal_create(cls, account: Account, name: str, semester: Semester, max_num_of_days: int) -> 'Timetable':
        common_info = TimetableCommonInfo.create(account=account, name=name)
        timetable, created = cls.objects.update_or_create(common_info=common_info, semester=semester,
                                                          defaults={'max_num_of_days': max_num_of_days})
        cls.log_created(timetable, created)
        return timetable

    def get_solutions(self, only_solved=True) -> QuerySet['TimetableSolution']:
        from plan_ilan.apps.timetable_generator.timetable_optimizer.optimizer_new import TimetableOptimizer
        if True or not self.solutions.exists():
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
        ordering = ['common_info', 'semester', 'created']
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


class TimetableSolution(TimeStampedModel, BaseModel):
    common_info = models.ForeignKey(TimetableCommonInfo, on_delete=models.CASCADE, related_name='solutions')
    lessons = models.ManyToManyField(Lesson, related_name='timetable_solutions')
    score = models.FloatField(editable=False)
    iterations = models.IntegerField(editable=False)
    is_solved = models.BooleanField(editable=False)

    @classmethod
    def create(cls, common_info: TimetableCommonInfo, ranked_lessons: QuerySet[RankedLesson], iterations: int,
               is_solved: bool, objective_score: float) -> 'TimetableSolution':
        solution, created = cls.objects.get_or_create(common_info=common_info, score=round(objective_score, 3),
                                                      iterations=iterations, defaults={'is_solved': is_solved})
        solution.lessons.set(ranked_lessons.values_list('lesson', flat=True))
        cls.log_created(solution, created)
        return solution

    @property
    def account(self):
        return self.common_info.account

    @property
    def name(self):
        return self.common_info.name

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

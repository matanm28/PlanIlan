from datetime import time
from typing import Union, List, Tuple

from django.db.models import QuerySet
from model_utils.models import TimeStampedModel

from plan_ilan.apps.timetable_generator.models import TimeInterval
from plan_ilan.apps.timetable_generator.models.ranked_lesson import RankedLesson
from plan_ilan.apps.timetable_generator.models.utils import Interval
from plan_ilan.apps.web_site.models import BaseModel, Account, Semester, Course, Lesson, Day
from django.db import models

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


class Timetable(TimeStampedModel, BaseModel):
    common_info = models.OneToOneField(TimetableCommonInfo, on_delete=models.CASCADE)
    mandatory_lessons = models.ManyToManyField(RankedLesson, related_name='timetables_mandatory')
    elective_lessons = models.ManyToManyField(RankedLesson, related_name='timetables_elective')
    blocked_time_periods = models.ManyToManyField('BlockedTimePeriod', related_name='timetables')
    elective_points_bound = models.ForeignKey(Interval, on_delete=models.CASCADE, related_name='timetables')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='timetables')
    max_num_of_days = models.IntegerField(default=7)

    @classmethod
    def create(cls, account: Account, name: str, mandatory_lessons: RankedLessonList,
               elective_lessons: RankedLessonList, blocked_time_periods: QuerySet['BlockedTimePeriod'],
               elective_points_bound: Interval, semester: Semester, max_num_of_days: int) -> 'Timetable':
        common_info = TimetableCommonInfo.create(account=account, name=name)
        timetable, created = cls.objects.get_or_create(common_info=common_info)
        timetable.update(elective_points_bound=elective_points_bound, semester=semester,
                         max_num_of_days=max_num_of_days)
        timetable.mandatory_lessons.set(mandatory_lessons)
        timetable.elective_lessons.set(elective_lessons)
        timetable.blocked_time_periods.set(blocked_time_periods)
        timetable.save()
        return timetable

    async def get_solutions(self, only_solved=True) -> QuerySet['TimetableSolution']:
        if not self.solutions.exists():
            optimizer = None
            # use optimizer
            # transform optimizer's answer to TimetableSolution and connect with CommonInfo.
        if only_solved:
            solutions = self.solutions.filter(is_solved=True)
        else:
            solutions = self.solutions
        return solutions.all()

    class Meta:
        ordering = ['common_info', 'semester', 'created']
        db_table = 'timetables'

    @property
    def courses(self) -> QuerySet[Course]:
        all_courses = list(self.mandatory_lessons.union(self.elective_lessons.all()))
        return Course.objects.filter(lessons__in=all_courses).distinct()

    @property
    def solutions(self):
        return self.common_info.solutions

    @property
    def account(self):
        return self.common_info.account

    @property
    def name(self):
        return self.common_info.name


class TimetableSolution(TimeStampedModel, BaseModel):
    common_info = models.ForeignKey(TimetableCommonInfo, on_delete=models.CASCADE, related_name='solutions')
    lessons = models.ManyToManyField(Lesson, related_name='timetable_solutions')
    score = models.FloatField(editable=False)
    iterations = models.IntegerField(editable=False)
    is_solved = models.BooleanField(editable=False)

    @classmethod
    def create(cls, common_info: TimetableCommonInfo, ranked_lessons: RankedLessonList, iterations: int,
               is_solved: bool) -> 'TimetableSolution':
        if isinstance(ranked_lessons, QuerySet):
            score = ranked_lessons.aggregate(score=models.Sum('rank'))['score']
        else:
            score = sum(ranked_lesson.rank for ranked_lesson in ranked_lessons)
        solution = cls.objects.create(common_info=common_info, score=score, iterations=iterations, is_solved=is_solved)
        cls.log_created(solution, True)
        return solution

    @property
    def account(self):
        return self.common_info.account

    @property
    def name(self):
        return self.common_info.name

    class Meta:
        ordering = ['created', 'modified', 'pk']
        db_table = 'solutions'
        verbose_name = 'solution'


class BlockedTimePeriod(BaseModel):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='blocked_times')
    blocked_time_periods = models.ManyToManyField(TimeInterval, related_name='blocked_time_periods')

    @classmethod
    def create(cls, day: Day, table: Timetable,
               blocked_times: List[Union[Tuple[time, time], TimeInterval]]) -> 'BlockedTimePeriod':
        blocked_time_period, created = cls.objects.get_or_create(day=day, timetable=table)
        cls.log_created(blocked_time_period, created)
        blocked_times_instances = []
        for blocked_time in blocked_times:
            if isinstance(blocked_time, TimeInterval):
                blocked_times_instances.append(blocked_time)
            else:
                time_interval = TimeInterval.create(*blocked_time)
                blocked_times_instances.append(time_interval)
        blocked_time_period.times.set(blocked_times_instances)
        return blocked_time_period

    class Meta:
        ordering = ['timetables', 'day']
        db_table = 'blocked_time_periods'

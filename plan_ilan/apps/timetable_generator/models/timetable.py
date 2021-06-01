from typing import Union, List

from django.db.models import QuerySet
from model_utils.models import TimeStampedModel

from plan_ilan.apps.timetable_generator.models.ranked_lesson import RankedLesson
from plan_ilan.apps.timetable_generator.models.utils import Interval, BlockedTimePeriod
from plan_ilan.apps.web_site.models import BaseModel, Account, Semester, Course, Lesson
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


class Timetable(TimeStampedModel, BaseModel):
    common_info = models.OneToOneField(TimetableCommonInfo, on_delete=models.CASCADE)
    mandatory_lessons = models.ManyToManyField(RankedLesson, related_name='timetables_elective')
    elective_lessons = models.ManyToManyField(RankedLesson, related_name='timetables_mandatory')
    blocked_time_periods = models.ManyToManyField(BlockedTimePeriod, on_delete=models.SET_NULL, null=True, blank=True)
    elective_points_bound = models.ForeignKey(Interval, on_delete=models.CASCADE, related_name='timetables')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='timetables')
    max_num_of_days = models.IntegerField(default=7)

    @classmethod
    def create(cls, account: Account, name: str, mandatory_lessons: RankedLessonList,
               elective_lessons: RankedLessonList, blocked_time_periods: QuerySet[BlockedTimePeriod],
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
        ordering = ['account', 'semester', 'name', 'created']
        db_table = 'timetables'

    @property
    def courses(self) -> QuerySet[Course]:
        all_courses = list(self.mandatory_lessons.union(self.elective_lessons.all()))
        return Course.objects.filter(lessons__in=all_courses).distinct()

    @property
    def solutions(self):
        return self.common_info.solutions


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

    class Meta:
        ordering = ['created', 'modified', 'pk']
        db_table = 'solutions'
        verbose_name = 'solution'

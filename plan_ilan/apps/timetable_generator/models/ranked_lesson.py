from django.db import models
from django.db.models import QuerySet

from plan_ilan.apps.web_site.models import Lesson, BaseModel, Course, LessonTime, LessonType, Teacher


class RankedLesson(BaseModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='ranked_lessons')
    rank = models.FloatField()

    class Meta:
        ordering = ['lesson', 'rank']
        db_table = 'ranked_lessons'

    @classmethod
    def create(cls, lesson: Lesson, rank: float = 1) -> 'RankedLesson':
        ranked_lesson = RankedLesson.objects.create(lesson=lesson, rank=rank)
        cls.log_created(ranked_lesson, True)
        return ranked_lesson

    @property
    def lesson_times(self) -> LessonTime:
        return self.lesson.session_times

    @property
    def course(self) -> Course:
        return self.lesson.course

    @property
    def code(self) -> str:
        return self.lesson.code

    @property
    def group(self) -> str:
        return self.lesson.group

    @property
    def lesson_type(self) -> LessonType:
        return self.lesson.lesson_type

    @property
    def teachers(self) -> QuerySet[Teacher]:
        return self.lesson.teachers

    @property
    def teacher(self) -> Teacher:
        return self.lesson.teacher

    @property
    def points(self) -> float:
        return self.lesson.points

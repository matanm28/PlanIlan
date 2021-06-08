from dataclasses import dataclass, field
from typing import List, Dict

from plan_ilan.apps.web_site.models import LessonTime, Lesson

from plan_ilan.apps.web_site.models import LessonTypeEnum, DAYS


@dataclass(unsafe_hash=True)
class OptimizedCourse:
    code: str
    group: str
    teacher: str
    session_type: LessonTypeEnum
    times: List[LessonTime]
    ranking: float = field(default=0.0, hash=False, compare=False)

    @classmethod
    def from_course_model(cls, lesson: Lesson, rankings: Dict = None):
        optimized_course = OptimizedCourse(lesson.code, lesson.group, lesson.teacher.title_and_name, lesson.lesson_type,
                                           lesson.session_times)
        if rankings:
            optimized_course.ranking = rankings[optimized_course.teacher] + rankings[optimized_course.code]
        return optimized_course

    @property
    def id(self) -> str:
        return f'{self.code}-{self.group}'

    @property
    def days_list(self) -> List[DAYS]:
        days = set()
        for time in self.times:
            days.add(time.day)
        return list(days)

    def __lt__(self, other: 'OptimizedCourse'):
        if self.ranking != other.ranking:
            return self.ranking < other.ranking
        if len(self.times) > 0 and len(other.times) > 0:
            return self.times[0].day < other.times[0].day
        elif len(self.times) > 0:
            return False
        else:
            return True

    def __le__(self, other: 'OptimizedCourse'):
        if self.ranking != other.ranking:
            return self.ranking <= other.ranking
        if len(self.times) > 0 and len(other.times) > 0:
            return self.times[0].day <= other.times[0].day
        elif len(self.times) > 0:
            return False
        else:
            return True

    def __gt__(self, other: 'OptimizedCourse'):
        return not self <= other

    def __ge__(self, other: 'OptimizedCourse'):
        return not self < other or self == other

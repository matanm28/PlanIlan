from dataclasses import dataclass, field
from typing import List, Dict

from PlanIlan.models import SessionTime, Course

from PlanIlan.models.enums import SessionTypeEnum, DayEnum


@dataclass(unsafe_hash=True)
class OptimizedCourse:
    code: str
    group: str
    teacher: str
    session_type: SessionTypeEnum
    times: List[SessionTime]
    ranking: float = field(default=0.0, hash=False, compare=False)

    @classmethod
    def from_course_model(cls, course: Course, rankings: Dict = None):
        optimized_course = OptimizedCourse(course.code, course.group, course.teacher.title_and_name, course.session_type,
                                           course.session_times)
        if rankings:
            optimized_course.ranking = rankings[optimized_course.teacher] + rankings[optimized_course.code]
        return optimized_course

    @property
    def id(self) -> str:
        return f'{self.code}-{self.group}'

    @property
    def days_list(self) -> List[DayEnum]:
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

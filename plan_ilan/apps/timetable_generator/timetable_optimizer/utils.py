from typing import List, Dict

from plan_ilan.apps.web_site.models import LessonTime


def single_overlap(course_times: List[LessonTime], spec_time: LessonTime) -> bool:
    for c_t in course_times:
        start = c_t.start_time
        end = c_t.end_time
        if start <= spec_time.start_time < end:
            return True
        if start < spec_time.end_time <= end:
            return True
    return False


def find_overlap(courses_by_day: Dict) -> List:
    lap_list = list()
    for course in courses_by_day:
        for check in courses_by_day:
            if course.id == check.id:
                continue
            times_of_course = course.times
            times_of_check = check.times
            overlap = False
            for time in times_of_course:
                overlap = single_overlap(times_of_check, time)
            if overlap:
                lap_list.append((course, check))
    return lap_list


class Interval:
    def __init__(self, left_bound: float = float('-inf'), right_bound: float = float('inf'), **kwargs):
        self._left = left_bound
        self._right = right_bound
        if left_bound > right_bound:
            self._left = right_bound
            self._right = left_bound
        self.bounds = {'left_closed': True, 'right_closed': True}
        for key in ['left_open', 'right_open'] + list(self.bounds.keys()):
            if key not in kwargs:
                continue
            if 'open' in key:
                self.bounds[key.replace('open', 'closed')] = not kwargs[key]
            else:
                self.bounds[key] = kwargs[key]

    @property
    def left(self) -> float:
        return self._left

    @property
    def right(self) -> float:
        return self._right

    @property
    def is_left_open(self) -> bool:
        return not self.bounds['left_closed']

    @property
    def is_right_open(self) -> bool:
        return not self.bounds['right_closed']

    @property
    def is_half_open(self) -> bool:
        return self.is_left_open or self.is_right_open

    @property
    def is_open(self) -> bool:
        return self.is_left_open and self.is_right_open

    @property
    def is_closed(self) -> bool:
        return self.bounds['left_closed'] and self.bounds['right_closed']

    @property
    def size(self) -> float:
        return self._right - self._left

from collections import defaultdict
from typing import List, Dict

from PlanIlan.models import SessionTime
from PlanIlan.models.enums import SessionType, Day
from PlanIlan.timetable_optimizer.optimized_course import OptimizedCourse


def cut_by_day(courses_list: List[OptimizedCourse]) -> List:
    days_to_courses_dict = defaultdict(list)
    for course in courses_list:
        for day in course.days_list:
            days_to_courses_dict[day].append(course)
    return days_to_courses_dict


def single_overlap(course_times: List[SessionTime], spec_time: SessionTime) -> bool:
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

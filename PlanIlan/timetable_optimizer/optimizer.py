from collections import defaultdict
from typing import List, Dict, Tuple

from pulp import *
from django.db.models import QuerySet

from PlanIlan.models import Course
from PlanIlan.timetable_optimizer.optimized_course import OptimizedCourse


class TimetableOptimizer:
    def __init__(self, mandatory: List[str], elective: List[str], blocked_times: Dict, rankings: Dict) -> None:
        self.mandatory_courses_codes = mandatory
        self.mandatory_dict = defaultdict(lambda: defaultdict(list))
        self.elective = elective
        self.elective_dict = defaultdict(lambda: defaultdict(list))
        self.blocked_times = blocked_times
        self.rankings = rankings
        self.day_to_hours_to_courses_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.model = LpProblem('Timetable', LpMaximize)
        self.post_init()

    def post_init(self):
        self.populate_courses_dicts()
        vars = self.create_lp_variables()
        self.populate_model(vars)

    @classmethod
    def get_courses_from_codes_list(cls, courses: List[str], rankings: Dict) -> List[OptimizedCourse]:
        courses_query_set = Course.objects.filter(code__in=courses)
        optimized_course_list = [OptimizedCourse.from_course_model(course, rankings) for course in courses_query_set]
        return optimized_course_list

    def get_courses_groups_stated(self):
        must_go_to = []
        for course_code in self.mandatory_courses_codes:
            courses = Course.objects.filter(code=course_code)
            session_types = courses[0].get_session_types()
            possible_combinations = courses
            if len(session_types) == 2:
                possible_combinations = [combi for combi in pl.allcombinations(courses, 2) if
                                         combi[0] != combi[1] and (combi[1].session_type, combi[2].session_type in session_types)]
            must_go_to.extend(possible_combinations)
        must = pl.LpVariable.dicts(f'mandatory', possible_combinations, 0, 1, pl.const.LpBinary)

    def populate_courses_dicts(self):
        courses = Course.objects.filter(code__in=self.mandatory_courses_codes)
        for course in courses:
            self.mandatory_dict[course.code][course.session_type.name].append(course)
        self.populate_day_to_hours_to_course_dict(courses)
        elective_courses = Course.objects.filter(code__in=self.elective)
        for course in elective_courses:
            self.elective_dict[course.code][course.session_type.name].append(course)
        self.populate_day_to_hours_to_course_dict(elective_courses)

    def populate_day_to_hours_to_course_dict(self, courses: QuerySet[Course]):
        for course in courses:
            for session_time in course.session_times.all():
                for hour in session_time.get_hours_list(jump=1, jump_by='hours'):
                    self.day_to_hours_to_courses_dict[session_time.semester][session_time.day][hour].append(course)
        return

    def populate_model(self, vars: Dict):
        ranks = []
        # for value in vars.values():
        self.model += lpSum([])

    def create_lp_variables(self):
        combs = []
        for key in self.mandatory_dict:
            temp = [self.mashu(combi) for combi in itertools.product(*list(self.mandatory_dict[key].values()))]
            combs.extend(temp)
        for key in self.elective_dict:
            temp = [self.mashu(combi) for combi in itertools.product(*list(self.elective_dict[key].values()))]
            combs.extend(temp)
        vars = LpVariable.dicts('courses', combs)
        return vars

    @staticmethod
    def mashu(t: Tuple):
        if len(t) == 2:
            return t[0].code_and_group, t[1].code_and_group
        return tuple(t[0].code_and_group)

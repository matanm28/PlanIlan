from collections import defaultdict
from typing import List, Dict, Tuple

from pulp import *
from django.db.models import QuerySet

from PlanIlan.models import Course
from PlanIlan.timetable_optimizer.optimized_course import OptimizedCourse
from PlanIlan.utils.general import name_of


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
        all_courses = self.populate_courses_dicts()
        self.populate_id_to_course_dict(all_courses)
        vars = self.create_lp_variables()
        self.populate_model(vars)

    @classmethod
    def get_courses_from_codes_list(cls, courses: List[str], rankings: Dict) -> List[OptimizedCourse]:
        courses_query_set = Course.objects.filter(code__in=courses)
        optimized_course_list = [OptimizedCourse.from_course_model(course, rankings) for course in courses_query_set]
        return optimized_course_list

    def populate_courses_dicts(self):
        mandatory_courses = Course.objects.filter(code__in=self.mandatory_courses_codes)
        for course in mandatory_courses:
            self.mandatory_dict[course.code][course.session_type.name].append(course)
        self.populate_day_to_hours_to_course_dict(mandatory_courses)
        elective_courses = Course.objects.filter(code__in=self.elective)
        for course in elective_courses:
            self.elective_dict[course.code][course.session_type.name].append(course)
        self.populate_day_to_hours_to_course_dict(elective_courses)
        return elective_courses + mandatory_courses

    def populate_day_to_hours_to_course_dict(self, courses: QuerySet[Course]):
        for course in courses:
            for session_time in course.session_times.all():
                for hour in session_time.get_hours_list(jump=1, jump_by='hours'):
                    self.day_to_hours_to_courses_dict[session_time.semester][session_time.day][hour].append(course)
        # todo: here just for breakpoint during debug.
        print(f'Finished {name_of([self.populate_id_to_course_dict])}')

    def populate_model(self, vars: Dict):
        objective = [self.__get_ranking_for_course_id(key) * var for key, var in vars.items()]
        self.model += lpSum(objective)
        # todo: create methods for days constraints and hours constraints (don't forget about semesters)

    def create_lp_variables(self):
        combs = []
        for key in self.mandatory_dict:
            products = self.__get_lists_cartesian_product(list(self.mandatory_dict[key].values()))
            temp = [self.__convert_course_tuple_to_ip(product) for product in products]
            combs.extend(temp)
        for key in self.elective_dict:
            products = self.__get_lists_cartesian_product(list(self.elective_dict[key].values()))
            temp = [self.__convert_course_tuple_to_ip(product) for product in products]
            combs.extend(temp)
        # todo: create vars as binary
        lp_vars = LpVariable.dicts('courses', combs)
        # we need to make sure that the tuple string representation for courses with both
        # TIRGUL and LECTURE is consistent, s.t one or the other always show up first, otherwise
        # it'll be mess to access the values every time.
        return lp_vars

    @staticmethod
    def __get_lists_cartesian_product(lists: List) -> List:
        if not lists:
            return []
        if len(lists) == 1:
            return itertools.product(lists[0])
        if len(lists) > 1:
            return itertools.product(*lists)

    @staticmethod
    def __convert_course_tuple_to_ip(course_tuple: Tuple):
        if len(course_tuple) == 2:
            return course_tuple[0].code_and_group, course_tuple[1].code_and_group
        return course_tuple[0].code_and_group,

    def __get_ranking_for_course_id(self, course_tuple: Tuple):
        if len(course_tuple) == 2:
            return self.rankings[course_tuple[0]] + self.rankings[course_tuple[1]]
        return self.rankings[course_tuple[0]]

    def populate_id_to_course_dict(self, courses_list: List[Course]):
        # todo: implement
        pass

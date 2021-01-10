from collections import defaultdict
from typing import List, Dict, Tuple

from codetiming import Timer
from pulp import *
from django.db.models import QuerySet
from gekko import *

from PlanIlan.models import Course, Day, Semester
from PlanIlan.timetable_optimizer.optimized_course import OptimizedCourse
from PlanIlan.utils.general import name_of


class TimetableOptimizer:
    def __init__(self, mandatory: List[str], elective: List[str], blocked_times: Dict, rankings: Dict,
                 elective_points_bound: Tuple[float, float] = (0, 10), max_days: int = 6) -> None:
        self.mandatory_dict = defaultdict(lambda: defaultdict(list))
        self.course_code_to_vars = defaultdict(list)
        self.id_to_course = {}
        self.max_days = max_days
        self.elective_dict = defaultdict(lambda: defaultdict(list))
        self.blocked_times = blocked_times
        self.rankings = rankings
        self.elective_points_bound = elective_points_bound
        self.semester_to_day_to_hours_to_courses_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.course_id_to_semester_and_days = defaultdict(list)
        self.model = Gekko(remote=False)
        self.course_vars = []
        self.days_vars = []
        self.post_init(mandatory, elective)

    def post_init(self, mandatory: List[str], elective: List[str]):
        all_courses = self.populate_courses_dicts(mandatory, elective)
        self.populate_id_to_course_dict(all_courses)
        courses_vars, day_vars = self.create_gekko_variables()
        self.populate_course_code_to_vars(courses_vars)
        self.populate_model(courses_vars, day_vars)
        self.course_vars = courses_vars
        self.days_vars = day_vars

    @Timer('solve')
    def solve(self):
        self.model.options.SOLVER = 1
        self.model.solve(disp=True, debug=True)
        solution = []
        for key, item in self.course_vars.items():
            if sum(item.VALUE.value) == 0:
                continue
            solution.extend(key)
        print(', '.join(solution))
        return solution

    @classmethod
    def get_courses_from_codes_list(cls, courses: List[str], rankings: Dict) -> List[OptimizedCourse]:
        courses_query_set = Course.objects.filter(code__in=courses)
        optimized_course_list = [OptimizedCourse.from_course_model(course, rankings) for course in courses_query_set]
        return optimized_course_list

    def populate_courses_dicts(self, mandatory: List[str], elective: List[str]):
        mandatory_courses = Course.objects.filter(code__in=mandatory)
        for course in mandatory_courses:
            self.mandatory_dict[course.code][course.session_type.name].append(course)
        self.populate_day_to_hours_to_course_dict(mandatory_courses)
        elective_courses = Course.objects.filter(code__in=elective)
        for course in elective_courses:
            self.elective_dict[course.code][course.session_type.name].append(course)
        self.populate_day_to_hours_to_course_dict(elective_courses)
        return list(elective_courses) + list(mandatory_courses)

    def populate_day_to_hours_to_course_dict(self, courses: QuerySet[Course]):
        for course in courses:
            for session_time in course.session_times.all():
                for hour in session_time.get_hours_list(jump=1, jump_by='hours'):
                    self.semester_to_day_to_hours_to_courses_dict[session_time.semester][session_time.day][hour].append(course)
                self.course_id_to_semester_and_days[course.code_and_group].append((session_time.semester.value,
                                                                                   session_time.day.value))
        # todo: here just for breakpoint during debug.
        print(f'Finished {name_of([self.populate_id_to_course_dict])}')

    def populate_model(self, courses_vars: Dict, days_vars: Dict):
        objective = [self.__get_ranking_for_course_id(key, days_vars) * var for key, var in courses_vars.items()]
        self.model.Maximize(self.sum(objective))
        # constraints must take mandatory courses
        for key in self.mandatory_dict:
            must_take_mandatory = []
            for t in courses_vars:
                if key not in t[0]:
                    continue
                must_take_mandatory.append(courses_vars[t])
            self.model.Equation(self.model.sum(must_take_mandatory) == 1)
        # constraint for taking the right amount of elective points
        course_code_to_points = self.__get_courses_code_to_points_dict()
        points_elective_constraint = []
        for course_code in self.elective_dict:
            for var_key in self.course_code_to_vars[course_code]:
                points_elective_constraint.append(course_code_to_points[course_code] * courses_vars[var_key])
        self.model.Equation(self.model.sum(points_elective_constraint) >= self.elective_points_bound[0])
        self.model.Equation(self.model.sum(points_elective_constraint) <= self.elective_points_bound[1])
        # todo: create methods for days constraints and hours constraints (don't forget about semesters)
        id_to_containing_vars = self.__id_to_containing_vars(courses_vars)
        zero = self.model.Const(0, 'zero')
        one = self.model.Const(1, 'one')
        for semester in self.semester_to_day_to_hours_to_courses_dict:
            day_courses_took_place = {}
            for day in self.semester_to_day_to_hours_to_courses_dict[semester]:
                courses_vars_in_day = []
                for hour in self.semester_to_day_to_hours_to_courses_dict[semester][day]:
                    for course in self.semester_to_day_to_hours_to_courses_dict[semester][day][hour]:
                        relevant_vars = [courses_vars[key] for key in id_to_containing_vars[course.code_and_group]]
                        courses_vars_in_day.extend(relevant_vars)
                        self.model.Equation(self.model.sum(relevant_vars) <= 1)
                day_courses_took_place[day] = courses_vars_in_day
            intermediate_days_vars = []
            for day in day_courses_took_place:
                i = self.model.Intermediate(self.model.if2(self.model.sum(day_courses_took_place[day]) - 1, zero, one),
                                            f'{semester, day}_inter')
                intermediate_days_vars.append(i)
            self.model.Equation(self.model.sum(intermediate_days_vars) <= self.max_days)
        # for semester in Semester:
        #     days_this_semester = [days_vars[semester.value, day.value] for day in Day]
        #     self.model.Equation(self.model.sum(days_this_semester) <= self.max_days)

    @staticmethod
    def sum(vars: List):
        result = 0
        for var in vars:
            result += var
        return result

    def create_gekko_variables(self):
        combs = []
        for key in self.mandatory_dict:
            products = self.__get_lists_cartesian_product(list(self.mandatory_dict[key].values()))
            temp = [self.__convert_course_tuple_to_ip(product) for product in products]
            combs.extend(temp)
        for key in self.elective_dict:
            products = self.__get_lists_cartesian_product(list(self.elective_dict[key].values()))
            temp = [self.__convert_course_tuple_to_ip(product) for product in products]
            combs.extend(temp)
        # we need to make sure that the tuple string representation for courses with both
        # TIRGUL and LECTURE is consistent, s.t one or the other always show up first, otherwise
        # it'll be mess to access the values every time.
        courses_vars = self.__create_dict_vars('courses', combs)
        semester_days_combs = list(itertools.product(Semester.values, Day.values))
        days_vars = self.__create_dict_vars('days', semester_days_combs)
        return courses_vars, days_vars

    def __create_dict_vars(self, name: str, entries: List, low_bound: int = 0, up_bound: int = 1):
        gekko_vars = {}
        for entry in entries:
            var = self.model.Var(lb=low_bound, ub=up_bound, integer=True, name=f'{name}_{entry}')
            gekko_vars[entry] = var
        return gekko_vars

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

    def __get_ranking_for_course_id(self, course_tuple: Tuple, days_vars: Dict):
        days = set(self.course_id_to_semester_and_days[course_tuple[0]])
        if len(course_tuple) == 2:
            ranking = self.rankings[course_tuple[0]] + self.rankings[course_tuple[1]]
            days = days | set(self.course_id_to_semester_and_days[course_tuple[1]])
        else:
            ranking = self.rankings[course_tuple[0]]
        return ranking
        # expression = ranking
        # for key in list(days):
        #     expression *= days_vars[key]
        # return expression

    def populate_id_to_course_dict(self, courses_list: List[Course]):
        for course in courses_list:
            self.id_to_course[course.code_and_group] = course

    def populate_course_code_to_vars(self, courses_vars: Dict):
        for course in list(self.mandatory_dict) + list(self.elective_dict):
            for t in courses_vars:
                if course in t[0]:
                    self.course_code_to_vars[course].append(t)

    def __get_courses_code_to_points_dict(self):
        course_code_to_points = {}
        for course in self.elective_dict:
            points = 0
            for session_type in self.elective_dict[course]:
                points += self.elective_dict[course][session_type][0].points
            course_code_to_points[course] = points
        return course_code_to_points

    @staticmethod
    def __id_to_containing_vars(courses_vars: Dict):
        id_to_containing_vars = defaultdict(list)
        for key in courses_vars:
            for t in key:
                id_to_containing_vars[t].append(key)
        return id_to_containing_vars

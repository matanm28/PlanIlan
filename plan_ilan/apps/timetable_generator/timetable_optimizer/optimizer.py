import itertools
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Union

from codetiming import Timer
from django.db.models import QuerySet
from gekko import Gekko

from plan_ilan.apps.web_site.models import Course, Lesson
from plan_ilan.apps.timetable_generator.timetable_optimizer.optimized_course import OptimizedCourse
from plan_ilan.apps.timetable_generator.timetable_optimizer.utils import Interval

EPSILON = 1e-3


class TimetableOptimizer:
    def __init__(self, mandatory: List[str], elective: List[str], blocked_times: Dict, rankings: Dict, semester: int,
                 elective_points_bound: Union[Interval, Tuple[float, float]] = (0, 20), max_days: int = 6) -> None:
        self.mandatory_dict = defaultdict(lambda: defaultdict(list))
        self.elective_dict = defaultdict(lambda: defaultdict(list))
        self.course_code_to_var_keys = defaultdict(list)
        self.max_days = max_days
        self.blocked_times = blocked_times
        self.rankings = self.__convert_rankings(rankings)
        self.semester = semester
        self.elective_points_bound = elective_points_bound if isinstance(elective_points_bound, Interval) else Interval(
            elective_points_bound[0], elective_points_bound[1])
        self.semester_to_day_to_hours_to_courses_dict = defaultdict(lambda: defaultdict(list))
        self.model = Gekko(remote=False)
        self.model_ready = False
        self.objective = []
        self.course_vars = {}
        self.__populate_courses_dicts(mandatory, elective)

    def __prepare_model_for_solve(self):
        self.__create_gekko_variables()
        self.__populate_course_code_to_vars()
        self.__populate_model()
        self.__solve_in_binary_mode()
        self.model_ready = True

    @Timer('solve')
    def solve(self) -> List[Tuple[List[str], Dict]]:
        if not self.model_ready:
            self.__prepare_model_for_solve()
        self.model.solve(debug=False)
        # so best solution is first
        solutions = deque()
        while self.is_solved:
            solution = self.__proccess_var_values_to_solution()
            meta_info = {'is_solved': self.is_solved, 'objective_score': self.objective_score, 'iterations': self.iterations}
            solutions.appendleft((solution, meta_info))
            # add objective to optimize better than last time
            self.model.Equation(self.model.sum(self.objective) > self.objective_score + EPSILON)
            # try starting from last solution values
            self.model.options.COLDSTART = 1
            self.model.solve(debug=False)
        return solutions

    def __proccess_var_values_to_solution(self):
        solution = []
        for key, item in self.course_vars.items():
            if sum(item.VALUE.value) == 1:
                solution.extend(key)
        return solution

    @classmethod
    def get_courses_from_codes_list(cls, courses: List[str], rankings: Dict) -> List[OptimizedCourse]:
        courses_query_set = Course.objects.filter(code__in=courses)
        optimized_course_list = [OptimizedCourse.from_course_model(course, rankings) for course in courses_query_set]
        return optimized_course_list

    def __populate_courses_dicts(self, mandatory: List[str], elective: List[str]) -> List[Course]:
        mandatory_courses = Lesson.objects.filter(course__code__in=mandatory)
        mandatory_courses_list = self.__build_dict_after_filtering(mandatory_courses, self.mandatory_dict)
        elective_courses = Lesson.objects.filter(course__code__in=elective)
        elective_courses_list = self.__build_dict_after_filtering(elective_courses, self.elective_dict)
        return mandatory_courses_list + elective_courses_list

    def __build_dict_after_filtering(self, courses_query_set: QuerySet[Lesson], courses_dict: Dict) -> List[Course]:
        courses_list = []
        for course in courses_query_set:
            if course.semester.number != self.semester:
                continue
            # to avoid REINFORCING types
            # todo: fix for later versions
            if course.points == 0:
                continue
            if self.is_course_at_blocked_times(course):
                continue
            courses_dict[course.code][course.lesson_type.label].append(course)
            courses_list.append(course)
        self.__populate_day_to_hours_to_course_dict(courses_list)
        return courses_list

    def __populate_day_to_hours_to_course_dict(self, courses: QuerySet[Lesson], jump: int = 1, jump_by: str = 'hours'):
        for course in courses:
            for session_time in course.session_times.all():
                for hour in session_time.get_hours_list(jump=jump, jump_by=jump_by):
                    self.semester_to_day_to_hours_to_courses_dict[session_time.day][hour].append(course)

    def __populate_model(self):
        self.objective = [self.__get_ranking_for_course_id(key) * var for key, var in self.course_vars.items()]
        self.model.Maximize(sum(self.objective))
        self.__define_must_take_every_mandatory_course_rules()
        self.__define_take_one_or_less_of_each_elective_course_rules()
        self.__define_elective_points_bounds_rules()
        self.__define_days_and_hours_rules()

    def __define_days_and_hours_rules(self):
        id_to_containing_vars = self.__id_to_containing_vars()
        zero = self.model.Const(0, 'zero')
        one = self.model.Const(1, 'one')
        max_days = self.model.Const(self.max_days, 'max_days')
        day_courses_took_place = {}
        for day in self.semester_to_day_to_hours_to_courses_dict:
            courses_vars_in_day = []
            for hour in self.semester_to_day_to_hours_to_courses_dict[day]:
                courses_in_hour = []
                for course in self.semester_to_day_to_hours_to_courses_dict[day][hour]:
                    relevant_vars = [self.course_vars[key] for key in id_to_containing_vars[course.code_and_group]]
                    courses_in_hour.extend(relevant_vars)
                self.model.Equation(self.model.sum(courses_in_hour) <= one)
                courses_vars_in_day.extend(courses_in_hour)
            day_courses_took_place[day] = courses_vars_in_day
        intermediate_days_vars = []
        for day in day_courses_took_place:
            i = self.model.Intermediate(self.model.if3(-self.model.sum(day_courses_took_place[day]), one, zero),
                                        f'{day.enum.name}_inter')
            intermediate_days_vars.append(i)
        self.model.Equation(self.model.sum(intermediate_days_vars) <= max_days)
        self.model.Equation(self.model.sum(intermediate_days_vars) > 0)

    def __define_elective_points_bounds_rules(self):
        # constraint for taking the right amount of elective points
        course_code_to_points = self.__get_courses_code_to_points_dict()
        points_elective_constraint = []
        for course_code in self.elective_dict:
            course_vars = [self.course_vars[var_key] for var_key in self.course_code_to_var_keys[course_code]]
            points_elective_constraint.append(self.model.sum(course_vars) * course_code_to_points[course_code])
        self.model.Equation(self.model.sum(points_elective_constraint) >= self.elective_points_bound.left)
        self.model.Equation(self.model.sum(points_elective_constraint) <= self.elective_points_bound.right)

    def __define_take_one_or_less_of_each_elective_course_rules(self):
        for course_code in self.elective_dict:
            take_only_one_elective = [self.course_vars[var_key] for var_key in self.course_code_to_var_keys[course_code]]
            # constraints for taking not more than one of the same elective course
            self.model.Equation(self.model.sum(take_only_one_elective) <= 1)

    def __define_must_take_every_mandatory_course_rules(self):
        for course_code in self.mandatory_dict:
            must_take_mandatory = [self.course_vars[var_key] for var_key in self.course_code_to_var_keys[course_code]]
            # constraints must take mandatory courses
            self.model.Equation(self.model.sum(must_take_mandatory) == 1)

    def __create_gekko_variables(self):
        combs = []
        for key in self.mandatory_dict:
            products = self.__get_lists_cartesian_product(list(self.mandatory_dict[key].values()))
            temp = [self.__convert_course_tuple_to_id(product) for product in products]
            combs.extend(temp)
        for key in self.elective_dict:
            products = self.__get_lists_cartesian_product(list(self.elective_dict[key].values()))
            temp = [self.__convert_course_tuple_to_id(product) for product in products]
            combs.extend(temp)
        # we need to make sure that the tuple string representation for courses with both
        # TIRGUL and LECTURE is consistent, s.t one or the other always show up first, otherwise
        # it'll be mess to access the values every time.
        self.course_vars = self.__create_dict_vars('courses', combs)

    def __create_dict_vars(self, name: str, entries: List, low_bound: int = 0, up_bound: int = 1) -> Dict:
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
    def __convert_course_tuple_to_id(course_tuple: Tuple):
        if len(course_tuple) == 2:
            return course_tuple[0].code_and_group, course_tuple[1].code_and_group
        return course_tuple[0].code_and_group,

    def __get_ranking_for_course_id(self, course_tuple: Tuple):
        if len(course_tuple) == 2:
            ranking = self.rankings[course_tuple[0]] + self.rankings[course_tuple[1]]
        else:
            ranking = self.rankings[course_tuple[0]]
        return ranking

    def __populate_course_code_to_vars(self):
        for course in list(self.mandatory_dict) + list(self.elective_dict):
            for var_key in self.course_vars:
                if course in var_key[0]:
                    self.course_code_to_var_keys[course].append(var_key)

    def __get_courses_code_to_points_dict(self):
        course_code_to_points = {}
        for course in self.elective_dict:
            points = 0
            for session_type in self.elective_dict[course]:
                points += self.elective_dict[course][session_type][0].points
            course_code_to_points[course] = points
        return course_code_to_points

    def __id_to_containing_vars(self):
        id_to_containing_vars = defaultdict(list)
        for key in self.course_vars:
            for t in key:
                id_to_containing_vars[t].append(key)
        return id_to_containing_vars

    def is_course_at_blocked_times(self, course: Course) -> bool:
        for session_time in course.session_times.all():
            day = str(session_time.day)
            if day not in self.blocked_times.keys():
                return False
            blocked_hour_at_day = self.blocked_times[day]
            for hour in session_time.get_hours_list(jump=1, jump_by='hours'):
                if str(hour) in blocked_hour_at_day:
                    return True
        return False

    @classmethod
    def __convert_rankings(cls, rankings: Dict) -> defaultdict:
        new_rankings = defaultdict(lambda: 1)
        for key, value in rankings.items():
            new_rankings[key] = value
        return new_rankings

    @property
    def objective_score(self) -> float:
        return abs(self.model.options.OBJFCNVAL)

    @property
    def is_solved(self) -> bool:
        return self.model.options.APPINFO == 0 and self.objective_score > 0

    @property
    def iterations(self) -> int:
        return self.model.options.ITERATIONS

    @property
    def max_iterations(self) -> int:
        return self.model.options.MAX_ITER

    @max_iterations.setter
    def max_iterations(self, value: int):
        if isinstance(value, int) and value >= 1:
            self.model.options.MAX_ITER = value

    def __solve_in_binary_mode(self):
        self.model.options.SOLVER = 1  # solves MINLP

    def solve_in_continuous_mode(self):
        self.model.options.SOLVER = 3

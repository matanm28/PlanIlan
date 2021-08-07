import itertools
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Union, Iterator

from codetiming import Timer
from django.db.models import QuerySet, Q
from gekko import Gekko

from plan_ilan.apps.timetable_generator.models import Timetable, BlockedTimePeriod, TimeInterval
from plan_ilan.apps.web_site.models import Lesson, Day, SemesterEnum

EPSILON = 1e-3


class TimetableOptimizer:
    def __init__(self, timetable: Timetable) -> None:
        self.timetable = timetable
        self.model = Gekko(remote=False)
        self.model_ready = False
        self.__is_done = False
        self.objective = []
        self.__solutions = deque()
        self.course_vars = {}

        self.mandatory_dict = defaultdict(lambda: defaultdict(list))
        self.elective_dict = defaultdict(lambda: defaultdict(list))
        self.course_code_to_var_keys = defaultdict(list)
        self.day_to_hours_to_courses_dict = defaultdict(lambda: defaultdict(list))

    @property
    def is_done(self) -> bool:
        return self.__is_done

    @property
    def solutions(self) -> List[Tuple[List[str], Dict]]:
        if not self.is_done:
            # todo: change to async
            raise ValueError('You need to solve before getting the solutions')
        return [(solution.copy(), meta_info.copy()) for solution, meta_info in self.__solutions]

    @property
    def max_days(self) -> int:
        return self.timetable.max_num_of_days

    @property
    def blocked_time_periods(self) -> QuerySet[BlockedTimePeriod]:
        return self.timetable.blocked_time_periods

    @property
    def valid_semesters(self) -> List[SemesterEnum]:
        return self.timetable.valid_semesters

    @property
    def elective_points_bound(self):
        return self.timetable.elective_points_bound

    def __prepare_model_for_solve(self):
        self.__populate_courses_dicts()
        self.__create_gekko_variables()
        self.__populate_course_code_to_vars()
        self.__populate_rankings()
        self.__populate_model()
        self.solve_in_binary_mode()
        self.model.solver_options = ['minlp_maximum_iterations 500', 'minlp_gap_tol 0.01', 'nlp_maximum_iterations 50']
        self.model.options.SEQUENTIAL = 0
        self.model.options.MAX_MEMORY = 8
        self.model.options.MAX_TIME = 10
        self.model.options.MAX_ITER = 500
        self.model.options.REDUCE = 10

        self.model_ready = True

    def solve(self) -> List[Tuple[List[str], Dict]]:
        if not self.model_ready:
            self.__prepare_model_for_solve()
        self.model.solve(debug=False)
        if not self.is_solved:
            # brute force again
            self.model.solve(debug=False)
        # so best solution is first
        while self.is_solved:
            self.__process_solution()
            # add objective to optimize better than last time
            self.model.Equation(self.model.sum(self.objective) > self.objective_score + EPSILON)
            # try starting from last solution values
            self.model.options.COLDSTART = 1
            self.solve_in_binary_mode()
            self.model.solve(debug=False)
        if not self.__solutions:
            self.model.options.RTOL = 1
            self.model.solve(debug=False)
            if self.is_solved:
                self.__process_solution()
        self.__is_done = True
        return self.solutions

    def __process_solution(self):
        solution = [var for key, item in self.course_vars.items() if sum(item.VALUE.value) == 1 for var in key]
        meta_info = {'is_solved': self.is_solved, 'objective_score': self.objective_score,
                     'iterations': self.iterations, 'possibly_invalid': self.model.options.RTOL == 1}
        self.__solutions.appendleft((solution, meta_info))

    @classmethod
    def __lessons_from_ranked_lessons(cls, lessons: QuerySet[Lesson]):
        return Lesson.objects.filter(pk__in=lessons.values_list('lesson', flat=True)).distinct()

    def __populate_courses_dicts(self):
        self.__build_dict_after_filtering(self.__lessons_from_ranked_lessons(self.timetable.mandatory_lessons),
                                          self.mandatory_dict)
        self.__build_dict_after_filtering(self.__lessons_from_ranked_lessons(self.timetable.elective_lessons),
                                          self.elective_dict)

    def __build_dict_after_filtering(self, lessons: QuerySet[Lesson], courses_dict: Dict):
        lessons_list = []
        for lesson in lessons.filter(session_times__semester__in=self.valid_semesters):
            # to avoid REINFORCING types
            # todo: fix for later versions
            if lesson.points == 0:
                continue
            if self.is_lesson_at_blocked_time(lesson):
                continue
            courses_dict[lesson.code][lesson.lesson_type.label].append(lesson)
            lessons_list.append(lesson)
        self.__populate_day_to_hours_to_course_dict(lessons_list)

    def __populate_day_to_hours_to_course_dict(self, lessons: Union[List[Lesson], QuerySet[Lesson]], jump: int = 1,
                                               jump_by: str = 'hours'):
        for lesson in lessons:
            for session_time in lesson.session_times.all():
                for hour in session_time.get_hours_list(jump=jump, jump_by=jump_by):
                    self.day_to_hours_to_courses_dict[session_time.day][hour].append(lesson)

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
        for day in self.day_to_hours_to_courses_dict:
            courses_vars_in_day = []
            for hour in self.day_to_hours_to_courses_dict[day]:
                courses_in_hour = []
                for course in self.day_to_hours_to_courses_dict[day][hour]:
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

    def __define_elective_points_bounds_rules(self):
        if not self.elective_dict:
            return
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
            take_only_one_elective = [self.course_vars[var_key] for var_key in
                                      self.course_code_to_var_keys[course_code]]
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
        self.course_vars = self.__create_dict_vars('courses', combs)

    def __create_dict_vars(self, name: str, entries: List, low_bound: int = 0, up_bound: int = 1) -> Dict:
        gekko_vars = {}
        # is set really needed?
        for entry in entries:
            var = self.model.Var(value=1, lb=low_bound, ub=up_bound, integer=True, name=f'{name}_{entry}')
            gekko_vars[entry] = var
        return gekko_vars

    @staticmethod
    def __get_lists_cartesian_product(lists: List) -> Iterator:
        if not lists:
            return []
        if len(lists) == 1:
            return itertools.product(lists[0])
        if len(lists) > 1:
            return itertools.product(*lists)

    @staticmethod
    def __convert_course_tuple_to_id(lessons: Tuple[Lesson]):
        return tuple(lesson.code_and_group for lesson in lessons)

    def __get_ranking_for_course_id(self, code_and_group_tuple: Tuple):
        return sum([self.rankings[code_and_group] for code_and_group in code_and_group_tuple])

    def __populate_course_code_to_vars(self):
        for code_and_group in list(self.mandatory_dict) + list(self.elective_dict):
            for var_key in self.course_vars:
                if code_and_group in var_key[0]:
                    self.course_code_to_var_keys[code_and_group].append(var_key)

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

    def is_lesson_at_blocked_time(self, lesson: Lesson) -> bool:
        common_days = Day.objects.filter(Q(number__in=lesson.days) & Q(number__in=self.timetable.blocked_days))
        if not common_days.exists():
            return False
        blocked_times = self.blocked_time_periods.filter(day__in=common_days)
        for blocked_time_period in TimeInterval.objects.filter(blocked_time_periods__in=blocked_times):
            for lesson_time in lesson.session_times.filter(day__in=common_days):
                t_interval = TimeInterval(start=lesson_time.start_time, end=lesson_time.end_time)
                if blocked_time_period.is_overlapping(t_interval):
                    return True
        return False

    def __populate_rankings(self):
        self.rankings = defaultdict(lambda: 1)
        for ranked_lesson in self.timetable.all_ranked_lessons:
            self.rankings[ranked_lesson.code_and_group] = ranked_lesson.rank

    @property
    def objective_score(self) -> float:
        return abs(self.model.options.OBJFCNVAL)

    @property
    def is_solved(self) -> bool:
        return self.model.options.SOLVESTATUS == 1 and self.objective_score > 0

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

    def solve_in_binary_mode(self):
        self.model.options.SOLVER = 1  # solves MINLP

    def solve_in_continuous_mode(self):
        self.model.options.SOLVER = 3

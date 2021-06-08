import json
from collections import defaultdict
from os import path

from argparse import ArgumentParser
from typing import Dict

from codetiming import Timer
from django.core.management import BaseCommand

from plan_ilan.apps.timetable_generator.models import Timetable
from plan_ilan.apps.web_site.models import SemesterEnum, DAYS, Course
from plan_ilan.apps.timetable_generator.timetable_optimizer.optimizer import TimetableOptimizer
from plan_ilan.apps.timetable_generator.timetable_optimizer.utils import Interval

DEFAULT_JSON_ENTRIES = {
    'rankings': defaultdict(lambda: 0),
    'mandatory': [],
    'elective': [],
    'max_days': 6,
    'semester': SemesterEnum.FIRST,
    'blocked_times': defaultdict(list),
    'elective_points_bound': Interval(0, 20)
}


def courses_parse_logic(courses: str):
    for delimiter in (',', ' '):
        if delimiter not in courses.strip():
            continue
        return parse_course_from_string(courses, delimiter)
    return []


def read_data_from_json(json_path: str, key: str):
    if not path.exists(path.realpath(json_path)):
        return None
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        if key not in data:
            return None
        return data[key]


def parse_course_from_string(courses: str, delimiter: str):
    return [course.strip() for course in courses.strip().split(delimiter)]


def rankings_parse_logic(rankings_path: str):
    data = read_data_from_json(rankings_path, 'rankings')
    return data if data is not None else {}


def blocked_times_parse_logic(blocked_times_path: str):
    data = read_data_from_json(blocked_times_path, 'blocked_times')
    return data if data is not None else {}


def parse_json_logic(json_path: str):
    res = DEFAULT_JSON_ENTRIES
    if path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        for key in data:
            res[key] = data[key]
    res['json_path'] = json_path
    return res


def Command():
    return OptimizeTimetableCommand()


class OptimizeTimetableCommand(BaseCommand):

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.driver = None

    @Timer(text='Script finished after total of {:.4f} seconds')
    def handle(self, *args, **options):
        t = Timetable.objects.first()
        t.get_solutions()
        if 'timetable_data' in options:
            data = options['timetable_data']
        else:
            data = options
        optimizer = TimetableOptimizer(data['mandatory'], data['elective'], data['blocked_times'], data['rankings'],
                                       data['semester'], data['elective_points_bound'], data['max_days'])
        solutions = optimizer.solve()
        endings = 'st nd rd'.split() + ('th ' * (len(solutions) - 3)).split()
        for i, (solution, meta_info) in enumerate(solutions):
            res = self.process_solution(solution)
            self.print_solution(res, meta_info)
            if 'json_path' in data:
                new_suffix = f'_output_{f"{i + 1}{endings[i]}_" if i > 0 else ""}best.json'
                self.output_as_json(res, data['json_path'].replace('.json', new_suffix), meta_info)

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-json-path', dest='timetable_data', type=parse_json_logic,
                            help='Path for JSON file containing the needed data')
        parser.add_argument('-mandatory', type=courses_parse_logic,
                            help="A comma\\space separated list of mandatory courses codes. Can't be empty")
        parser.add_argument('-elective', type=courses_parse_logic, default=[],
                            help="A comma\\space separated list of elective courses codes.")
        parser.add_argument('-ranking_path', dest='rankings', type=rankings_parse_logic,
                            help="Path for JSON file containing the rankings for the given courses.")
        parser.add_argument('-blocked_times_path', dest='blocked_times', type=blocked_times_parse_logic, default={},
                            help="Path for JSON file containing a set of blocked times")
        parser.add_argument('-max_timetables', type=int, action='store', default=1)

    @staticmethod
    def process_solution(solution):
        courses = []
        results = [s.split('-') for s in solution]
        for code, group in results:
            courses.extend(Course.objects.filter(code=code, group=group))
        semester_to_day_to_hours_to_courses_dict = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        for course in courses:
            for session_time in course.session_times.all():
                for hour in session_time.get_hours_list(jump=1, jump_by='hours'):
                    semester_to_day_to_hours_to_courses_dict[session_time.semester][session_time.day][hour] = course
        return semester_to_day_to_hours_to_courses_dict

    @staticmethod
    def print_solution(semester_to_day_to_hours_to_courses: Dict, meta_info: Dict):
        meta = '\n'.join(['Meta-Info:'] + [f'{k.replace("_", " ").capitalize()}: {v}' for k, v in meta_info.items()])
        print(meta)
        for semester in sorted(semester_to_day_to_hours_to_courses):
            print(f'Semester {semester}')
            for day in sorted(semester_to_day_to_hours_to_courses[semester]):
                print(f'{DAYS.from_int(day).name}:')
                for hour in sorted(semester_to_day_to_hours_to_courses[semester][day]):
                    print(f'{hour}: {semester_to_day_to_hours_to_courses[semester][day][hour]}')

    def output_as_json(self, res: Dict, json_output_path: str, meta_info: Dict):
        json_dict = {'META_INFO': meta_info}
        timetable_dict = {}
        json_dict['timetable'] = timetable_dict
        for semester in sorted(res):
            semester_name = SemesterEnum.from_int(semester).name
            timetable_dict[semester_name] = {}
            for day in sorted(res[semester]):
                day_name = DAYS.from_int(day).name
                timetable_dict[semester_name][day_name] = {}
                for hour in sorted(res[semester][day]):
                    timetable_dict[semester_name][day_name][str(hour)] = str(res[semester][day][hour])
        with open(json_output_path, 'w', encoding='utf-8') as output_file:
            json.dump(json_dict, output_file, indent=1, ensure_ascii=False)

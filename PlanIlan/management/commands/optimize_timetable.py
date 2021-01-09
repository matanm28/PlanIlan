# 89550,89220,89214,89132,89226,89230,89262,89350,89362,89210,89256,89211,89231

import sys
import json
from os import path

from argparse import ArgumentParser

from codetiming import Timer
from django.core.management import BaseCommand

from PlanIlan.timetable_optimizer.optimizer import TimetableOptimizer


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


class Command(BaseCommand):

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.driver = None

    @Timer(text='Script finished after total of {:.4f} seconds')
    def handle(self, *args, **options):
        optimizer = TimetableOptimizer(options['mandatory'], options['elective'], options['blocked_times'], options['rankings'])
        print(optimizer)

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-mandatory', type=courses_parse_logic, required=True,
                            help="A comma\\space separated list of mandatory courses codes. Can't be empty")
        parser.add_argument('-elective', type=courses_parse_logic, default=[],
                            help="A comma\\space separated list of elective courses codes.")
        parser.add_argument('-ranking_path', dest='rankings', type=rankings_parse_logic,
                            help="Path for JSON file containing the rankings for the given courses.")
        parser.add_argument('-blocked_times_path', dest='blocked_times', type=blocked_times_parse_logic, default={},
                            help="Path for JSON file containing a set of blocked times")
        parser.add_argument('-max_timetables', type=int, action='store', default=1)

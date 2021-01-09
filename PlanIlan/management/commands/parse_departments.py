import os
import sys
from argparse import ArgumentParser
from collections import defaultdict, deque
from typing import List, Set, Dict

from django.core.management import BaseCommand
from selenium.common.exceptions import NoSuchElementException

from PlanIlan.models import Course
from PlanIlan.utils.letters import big_letters
from PlanIlan.utils.web import *
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import re
import json


class Command(BaseCommand):

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.driver = None

    def handle(self, *args, **options):
        if options['parse_enums']:
            self.run(options['json_file_path'])
        if options['gen_enum_file'] or not options['parse_enums']:
            self.parse_department_enums_as_python_code('department_enums.txt')

    def add_arguments(self, parser:ArgumentParser):
        parser.add_argument('json_file_path', type=str, help='File path for output')
        parser.add_argument('--gen_enum_file', dest='gen_enum_file', action='store_true', default=False)
        parser.add_argument('--only_enum_file', dest='parse_enums', action='store_false', default=True)

    def run(self, json_file_path: str):
        self.driver = get_chrome_driver(True)
        base_url = 'https://shoham.biu.ac.il/BiuCoursesViewer/'
        self.driver.get(base_url)
        select = Select(self.driver.find_element_by_id('ContentPlaceHolder1_cmbDepartments'))
        department_name_to_numbers = defaultdict(list)
        options_list = [option.text for option in select.options]
        for option in options_list:
            if option == 'בחר':
                continue
            select.select_by_visible_text(option)
            self.driver.find_element_by_id('ContentPlaceHolder1_btnSearch').click()
            department_name_to_numbers[option].extend(self.get_departments_code())
            self.driver.get(base_url)
            select = Select(self.driver.find_element_by_id('ContentPlaceHolder1_cmbDepartments'))
        self.print_dict(department_name_to_numbers)
        if not json_file_path:
            json_file_path = 'faculty_names_and_numbers.json'
        if not json_file_path.endswith('.json'):
            json_file_path += '.json'
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(department_name_to_numbers, file, ensure_ascii=False, indent=4)
        print(big_letters('success', 2, 4))

    def get_departments_code(self) -> List[str]:
        soups = self.parse_all_pages_to_soup()
        faculty_numbers_set = self.parse_faculty_numbers_from_soups(soups)
        return faculty_numbers_set

    def parse_all_pages_to_soup(self) -> List[BeautifulSoup]:
        parser = 'html.parser'
        soups = []
        try:
            pagination_tr = self.driver.find_element_by_css_selector('.cssPager')
            pagination_text = pagination_tr.text
        except NoSuchElementException:
            pagination_text = ''
        pages_numbers = deque(pagination_text.strip('>>').split())
        last_page_number = '0'
        while len(pages_numbers) > 0:
            page_number = pages_numbers.popleft()
            if page_number not in ('1', '...'):
                elements = self.driver.find_elements_by_link_text(page_number)
                if len(elements) == 1:
                    elements[0].click()
                else:
                    print(f'Error on {self.driver.current_url} with page number {page_number}', file=sys.stderr)
            if page_number == '...':
                elements = self.driver.find_elements_by_link_text('...')
                if len(elements) == 2:
                    elements[1].click()
                elif len(elements) == 1 and last_page_number == '10':
                    elements[0].click()
                else:
                    continue
                pagination_tr = self.driver.find_element_by_css_selector('.cssPager')
                pagination_text = pagination_tr.text
                last_page_number = int(last_page_number)
                for item in pagination_text.strip('>> <<').lstrip('...').split():
                    if item == '...' or item.isnumeric() and int(item) > last_page_number:
                        pages_numbers.append(item)
                page_number = pages_numbers.popleft()
            soups.append(BeautifulSoup(self.driver.page_source, parser))
            last_page_number = page_number
        assert int(last_page_number) == len(soups)
        return soups

    def parse_faculty_numbers_from_soups(self, soups: List[BeautifulSoup]) -> Set[str]:
        id_regex = re.compile('ContentPlaceHolder1_gvLessons_lblLessonCode', re.IGNORECASE)
        courses_codes = []
        for soup in soups:
            tags = soup.find_all(id=id_regex)
            courses_codes.extend([tag.text for tag in tags])
        faculty_numbers = [Course.get_faculty_code_from_course_id(course_code) for course_code in courses_codes]
        return set(faculty_numbers)

    def print_dict(self, department_name_to_numbers: defaultdict):
        results = []
        for key in department_name_to_numbers:
            if not department_name_to_numbers[key]:
                continue
            temp_str = '\n'.join([f'= {number}, _("{key}")' for number in department_name_to_numbers[key]])
            results.append(temp_str)
        print('\n'.join(results))

    def load_from_dict_from_json(self, json_file_path: str) -> Dict:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            faculty_names_and_numbers = json.load(file)
            return faculty_names_and_numbers

    def parse_department_enums_as_python_code(self, file_path: str) -> str:
        with open('label_to_param_name.json', 'r', encoding='utf-8') as file:
            label_to_param_name = json.load(file)
        with open('faculty_names_and_numbers.json', 'r', encoding='utf-8') as file:
            department_name_to_numbers = json.load(file)
        params_lines = []
        for i,name in enumerate(department_name_to_numbers):
            params_lines.append(f"{label_to_param_name[name]} = {i}, _('{name}')")
            enums_string = '\n'.join(params_lines)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(enums_string)
        return enums_string

import concurrent
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

from codetiming import Timer
from django.core.management import BaseCommand

from PlanIlan.data_mining.shoham_crawler import ShohamCrawler

from PlanIlan.models import Course
from PlanIlan.models.enums import Department
from PlanIlan.utils.letters import big_letters


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.run(options['base_url'], options['num_of_crawlers'], options['run_with_threads'])

    def add_arguments(self, parser):
        parser.add_argument('-base_url', type=str, action='store',
                            help='The url leading to Bar-Ilan Shoham site main page',
                            default='https://shoham.biu.ac.il/BiuCoursesViewer/')
        parser.add_argument('-num_of_crawlers', type=int, action='store',
                            help='The number of crawlers to instantiate.', default=4)
        parser.add_argument('--run_with_single_thread', dest='run_with_threads', action='store_false', default=True)


    @classmethod
    @Timer(text='Script finished after total of {:.4f} seconds', logger=logging.info)
    def run(cls, base_url: str, num_of_crawlers: int, run_with_threads: bool):
        courses = []
        if run_with_threads:
            with ThreadPoolExecutor(num_of_crawlers) as executor:
                futures = {}
                for department in Department:
                    if department == Department.NULL_DEPARTMENT:
                        continue
                    future = executor.submit(cls.run_single_crawler, base_url, department.label, run_with_threads)
                    futures[future] = department
                for future in concurrent.futures.as_completed(futures.keys()):
                    if future.exception():
                        logging.error(f'Department {futures[future].label} ended with exception')
                        logging.debug(f'{future.exception()}')
                        continue
                    courses.extend(future.result())
        else:
            courses = cls.run_single_crawler(base_url, 'בחר', run_with_threads)
        logging.info(f'Parsed total of {len(courses)} courses')
        print(big_letters('finished', 2, 4))

    @classmethod
    def run_single_crawler(cls, base_url: str, department_name: str, run_with_threads: bool) -> List[Course]:
        # todo maybe add debug flag - check if implemented in django.
        crawler = ShohamCrawler(base_url, False)
        crawler.start(department_name, run_with_threads)
        return crawler.courses_list

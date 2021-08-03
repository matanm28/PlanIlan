import concurrent
import logging
from concurrent.futures import ThreadPoolExecutor

from codetiming import Timer
from django.core.management import BaseCommand

from plan_ilan.data_mining.courses.shoham_crawler import ShohamCrawler
from plan_ilan import settings

from plan_ilan.apps.web_site.models import Course, DepartmentEnum
from plan_ilan.utils.letters import big_letters

logger = logging.getLogger(__name__)


def Command():
    return PopulateDatabaseCommand()


class PopulateDatabaseCommand(BaseCommand):

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super(PopulateDatabaseCommand, self).__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        self.run(options['base_url'], options['num_of_crawlers'], options['run_with_threads'],
                 options['run_with_thread_pool'])

    def add_arguments(self, parser):
        parser.add_argument('-base_url', type=str, action='store',
                            help='The url leading to Bar-Ilan Shoham site main page',
                            default='https://shoham.biu.ac.il/BiuCoursesViewer/')
        parser.add_argument('-num_of_crawlers', type=int, action='store',
                            help='The number of crawlers to instantiate.', default=3)
        parser.add_argument('--run_with_single_thread', dest='run_with_threads', action='store_false', default=True)
        parser.add_argument('--run_without_thread_pool', dest='run_with_thread_pool', action='store_false',
                            default=True)

    @classmethod
    @Timer(text='Script finished after total of {:.4f} seconds', logger=logger.info)
    def run(cls, base_url: str, num_of_crawlers: int, run_with_threads: bool, run_with_thread_pool: bool):
        courses_list = []
        if run_with_thread_pool:
            departments_with_fails = []
            departments_with_errors = []
            with ThreadPoolExecutor(num_of_crawlers) as executor:
                futures = {}
                for department in DepartmentEnum:
                    if department == DepartmentEnum.NULL_DEPARTMENT:
                        continue
                    future = executor.submit(cls.run_single_crawler, base_url, department.label, run_with_threads)
                    futures[future] = department
                    logger.info(f'sent {department.label} to executor')
                for future in concurrent.futures.as_completed(futures.keys()):
                    if future.exception():
                        failed_department = futures[future]
                        logger.error(f'Department {failed_department.label} ended with exception')
                        logger.exception(f'{future.exception()}')
                        departments_with_errors.append(failed_department)
                        continue
                    crawler = future.result()
                    courses = crawler.courses_list
                    courses_list.extend(courses)
                    logger.info(f'Processed {len(courses)} courses from department {futures[future]}')
                    if crawler.num_of_fails:
                        departments_with_fails.append(futures[future])
                if departments_with_errors:
                    departments_error_string = '\n'.join(
                        [f'{dep.number}.{dep.label}' for dep in departments_with_errors])
                    logger.error(f'Departments that exited with exceptions:\n {departments_error_string}')
                if departments_with_fails:
                    departments_fails_string = '\n'.join(
                        [f'{dep.number}.{dep.label}' for dep in departments_with_fails])
                    logger.error(f'Departments that failed to insert some data:\n {departments_fails_string}')
        else:
            crawler = cls.run_single_crawler(base_url, 'בחר', run_with_threads)
        logger.info(f'Parsed total of {len(crawler.courses_list)} courses.')
        print(big_letters('finished', 2, 4))

    @classmethod
    def run_single_crawler(cls, base_url: str, department_name: str, run_with_threads: bool) -> ShohamCrawler:
        crawler = ShohamCrawler(base_url, False and settings.DEBUG, logger)
        crawler.start(department_name, run_with_threads)
        return crawler

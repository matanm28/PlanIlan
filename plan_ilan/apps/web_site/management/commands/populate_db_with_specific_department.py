import logging

from codetiming import Timer

from plan_ilan.apps.web_site.management.commands.populate_database import PopulateDatabaseCommand
from plan_ilan.apps.web_site.models import DepartmentEnum
from plan_ilan.utils.letters import big_letters

logger = logging.getLogger('plan_ilan.management.commands.populate_database')


def Command():
    return PopulateDatabaseWithSpecificDepartment()


class PopulateDatabaseWithSpecificDepartment(PopulateDatabaseCommand):

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super(PopulateDatabaseWithSpecificDepartment, self).__init__(stdout, stderr, no_color, force_color)

    @Timer(text='Script finished after total of {:.4f} seconds', logger=print)
    def handle(self, *args, **options):
        for department in options['departments']:
            department_enum = DepartmentEnum.from_int(department)
            if department_enum == DepartmentEnum.NULL_DEPARTMENT:
                continue
            logger.info(f'Started processing {department_enum.label}')
            crawler = self.run_single_department(options['base_url'], options['run_with_threads'],
                                                 department_enum)
            logger.info(f'Processed {len(crawler.courses_list)} courses from {department_enum.label}')
        print(big_letters('finished', 2, 4))

    def add_arguments(self, parser):
        super(PopulateDatabaseWithSpecificDepartment, self).add_arguments(parser)
        parser.add_argument('-d', '--departments', action='extend', nargs='+', type=int)

    def run_single_department(self, base_url: str, run_with_threads: bool, department: DepartmentEnum):
        crawler = self.run_single_crawler(base_url, department.label, run_with_threads)
        return crawler

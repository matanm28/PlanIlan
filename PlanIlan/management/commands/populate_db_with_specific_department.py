import logging
from typing import Union

from codetiming import Timer

from PlanIlan.management.commands.populate_database import PopulateDatabaseCommand
from PlanIlan.models import Department
from PlanIlan.utils.letters import big_letters


logger = logging.getLogger(__name__)

def Command():
    return PopulateDatabaseWithSpecificDepartment()


class PopulateDatabaseWithSpecificDepartment(PopulateDatabaseCommand):

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super(PopulateDatabaseWithSpecificDepartment, self).__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        self.run_single_department(options['base_url'], options['run_with_threads'], options['department'])

    def add_arguments(self, parser):
        super(PopulateDatabaseWithSpecificDepartment, self).add_arguments(parser)
        parser.add_argument('-d', '--department', type=int, default=Department.COMPUTER_SCIENCE)

    @Timer(text='Script finished after total of {:.4f} seconds', logger=logger.info)
    def run_single_department(self, base_url: str, run_with_threads: bool, department: int):
        courses = self.run_single_crawler(base_url, Department.from_int(department).label, run_with_threads)
        print(big_letters('finished', 2, 4))

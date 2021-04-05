from django.core.management import BaseCommand

from PlanIlan.data_mining.staff.staff_crawler import StaffCrawler
from PlanIlan.models import Department
from PlanIlan.models.enums import Faculty
from PlanIlan.data_mining.staff.lookup_parameters import *


def Command():
    return PopulateStaffCommand()


class PopulateStaffCommand(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        url = 'https://math.biu.ac.il/senior-faculty'
        department = Department.MATHEMATICS
        faculty = "מדעים מדוייקים"
        items_class = 'views-tr'
        key_to_class = {
            'photo': 'views-td--field-person-picture',
            'title': 'views-td--field-person-title',
            'name': 'views-td--title',
            'office': 'views-td--field-person-office',
            'phone': 'views-td--field-person-phone',
            'email': 'views-td--field-text-email',
            'website': 'views-td--field-person-website',
        }
        crawler = StaffCrawler(url, Faculty.NONE, department, items_class, key_to_class, has_photos=True,
                               email_suffix='@math.biu.ac.il')
        l = crawler.crawl()
        print(l)
        input('press to continue...')

    def add_arguments(self, parser):
        pass

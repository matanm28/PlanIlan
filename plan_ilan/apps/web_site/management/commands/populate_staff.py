from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.management import BaseCommand

from plan_ilan.data_mining.staff.staff_crawler import StaffCrawler
from plan_ilan.apps.web_site.models import DepartmentEnum, Teacher,FacultyEnum, TitleEnum, Title, Faculty
from plan_ilan.data_mining.staff.lookup_parameters import *


def Command():
    return PopulateStaffCommand()


class PopulateStaffCommand(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        url = 'https://math.biu.ac.il/senior-faculty'
        department = DepartmentEnum.MATHEMATICS
        faculty = FacultyEnum.EXACT_SCIENCES
        key_to_class = {
            'photo': {'key': '.field-person-picture img', 'selector': 'select'},
            'title': 'views-td--field-person-title, ',
            'name': 'views-td--title',
            'office': 'field-person-office',
            'phone': {
                'key': '.field--field-person-phone .field__item',
                'selector': 'select'
            },
            'email': 'div.field__item--field-text-email, div.field__item--field-person-email',
            'website': 'field__item--field-person-website',
        }
        staff_dict = {'params': key_to_class,
                      'persons': 'views-tr',
                      'details_url': {
                          'key': '.views-td--title a',
                          'selector': 'select'
                      }
                      }
        staff_lookup = StaffLookup.from_dict(staff_dict)
        crawler = StaffCrawler(url, department, staff_lookup, email_suffix='@math.biu.ac.il')
        l = crawler.crawl()
        teachers_data = crawler.get_teachers_data()
        faculty = Faculty.get_from_enum(faculty)
        for data in teachers_data:
            title_enum = TitleEnum.from_string(data.title)
            title = Title.get_from_enum(title_enum)
            teacher = Teacher.create(data.name, title, faculty)
            
            teacher.phone = data.phone
            teacher.office = data.office
            teacher.email = data.email
            teacher.website_url = data.website

            buffer = BytesIO()
            data.photo.save(buffer, format='jpeg')
            pic = ContentFile(buffer.getvalue())

            teacher.image.save('profile.jpg',
                               InMemoryUploadedFile(pic, None, 'profile.jpg', 'image/jpeg', pic.tell, None))
            teacher.save()

    def add_arguments(self, parser):
        pass

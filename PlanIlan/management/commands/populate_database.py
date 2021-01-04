from django.core.management import BaseCommand

from PlanIlan.data_mining.shoham_crawler import ShohamCrawler
from PlanIlan.utils.letters import big_letters


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.run()

    @staticmethod
    def run():
        crawler = ShohamCrawler('https://shoham.biu.ac.il/BiuCoursesViewer/')
        crawler.populate_html_pages_from_course_viewer()
        crawler.open_window = True
        crawler.parse_all_content()
        print(big_letters('success', 2, 4))

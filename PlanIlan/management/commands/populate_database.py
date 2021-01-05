from django.core.management import BaseCommand

from PlanIlan.data_mining.shoham_crawler import ShohamCrawler
from PlanIlan.utils.letters import big_letters


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.run()

    @staticmethod
    def run():
        crawler = ShohamCrawler('https://shoham.biu.ac.il/BiuCoursesViewer/', True)
        crawler.start()
        print(big_letters('success', 2, 4))

import time
from typing import List

from bs4 import BeautifulSoup
import re
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from PlanIlan.models import Course, Location, Day, LessonTime, Teacher


class ShohamCrawler:
    __hour_regex = '[0-9][0-9]:[0-9][0-9] - [0-9][0-9]:[0-9][0-9]'
    __time_format = '%H:%M'

    def __init__(self, base_url: str):
        logging.info('Creating a ShoamCrawler instance')
        self.__courses_list = []
        self.__teachers_list = []
        self.__html_links = []
        self.__soups_list = []
        self.__base_url = base_url
        self.__print_soup = False
        self.__open_window = False
        logging.info('Finished creating a ShoamCrawler instance')

    @property
    def courses_list(self) -> List[Course]:
        return self.__courses_list

    @property
    def html_links(self) -> List[str]:
        return self.__html_links

    @property
    def soups_list(self) -> List[BeautifulSoup]:
        return self.__soups_list

    @property
    def base_url(self) -> str:
        return self.__base_url

    @base_url.setter
    def base_url(self, value: str):
        self.__base_url = value

    @property
    def hour_regex(self):
        return self.__hour_regex

    @property
    def time_format(self):
        return self.__time_format

    @property
    def print_soup(self) -> bool:
        return self.__print_soup

    @print_soup.setter
    def print_soup(self, value: bool):
        self.__print_soup = value

    @property
    def open_window(self) -> bool:
        return self.__open_window

    @open_window.setter
    def open_window(self, value: bool):
        self.__open_window = value

    @property
    def debug(self) -> bool:
        return self.open_window or self.print_soup

    @debug.setter
    def debug(self, value: bool):
        self.print_soup = value
        self.open_window = value

    def add_html_page(self, link: str):
        self.html_links.append(link)

    def add_page_to_soup_list(self, content: str):
        self.soups_list.append(BeautifulSoup(content, 'html.parser'))

    def parse_single_course_page(self, soup: BeautifulSoup) -> List[Course]:
        if self.print_soup:
            print(soup.prettify())
        table = soup.find(attrs={'class': 'resulte_table'})
        for tr in table.tbody.contents[2:-1]:
            if len(tr.contents) != 11:
                continue
            code = str(tr.contents[1].text.strip())
            course_name = tr.contents[2].text.strip()
            group_code = str(tr.contents[3].text.strip())
            id = code + group_code
            teacher_title, teacher_name = tr.contents[4].text.strip().split(' ')
            if not teacher_name or not teacher_title:
                continue
            session_type = tr.contents[5].text.strip()
            if not session_type:
                continue
            semester = tr.contents[6].text.strip()
            if not semester:
                continue
            elif 'א' in semester and 'ב' in semester:
                semester = 'שנתי'
            days = tr.contents[7].text.strip().split(',')
            if not days or not self.__all_days_valid(days):
                continue
            hours = re.findall(self.hour_regex, tr.contents[8].text.strip())
            if len(hours) == 0:
                continue
            lesson_time_list = self.parse_lesson_times(days, hours)
            link = f"https://shoham.biu.ac.il/BiuCoursesViewer/{tr.contents[9].find('a', href=True)['href']}"
            teacher = Teacher.create(name=teacher_name,teacher_title=teacher_title)
            course = Course.create(course_id=id, name=course_name,teacher=teacher,lesson_times=lesson_time_list,
                                   locations=)
            page_courses_list.append(course)
        return page_courses_list

    def parse_all_content(self):
        driver = ShohamCrawler.__get_chrome_driver()
        for page in self.htmlPageContents:
            page_courses = self.parse_single_course_page(page)
            for course in page_courses:
                driver.get(course.details_link)
                building_place_holder = '//*[@id="ContentPlaceHolder1_tdBuilding"]/table/tbody/tr/td'
                class_number_place_holder = '//*[@id="ContentPlaceHolder1_tdRoom"]/table/tbody/tr/td'
                try:
                    building = driver.find_element_by_xpath(building_place_holder).text
                except:
                    building = 'אין מידע'
                try:
                    class_number = driver.find_element_by_xpath(class_number_place_holder).text
                except:
                    class_number = 'אין מידע'
                course.location = ShohamCrawler.parse_location(building, class_number)
                logging.info(
                    f'Done processing course with code:{course.code}, group:{course.group_code}, '
                    f'name:{course.name}')
                self.coursesList.append(course)
        driver.close()
        logging.info('Closed ChromeWebDriver')

    def populate_html_pages_from_course_viewer(self, faculty_name):
        logging.info('Started populating html pages from courses viewer')
        driver = ShohamCrawler.__get_chrome_driver()
        url = "https://shoham.biu.ac.il/BiuCoursesViewer/MainPage.aspx"
        driver.get(url)
        faculty_place_holder = '//*[@id="ContentPlaceHolder1_cmbDepartments"]'
        search = '//*[@id="ContentPlaceHolder1_btnSearch"]'
        driver.find_element_by_xpath(faculty_place_holder).send_keys(faculty_name)
        driver.find_element_by_xpath(search).click()
        html = driver.page_source
        self.add_page_to_soup_list(BeautifulSoup(html, 'html.parser'))

        for i in range(2, 490):
            try:
                elem = driver.find_element_by_link_text(i.__str__())
            except NoSuchElementException:
                elements = driver.find_elements_by_link_text('...')
                if i > 11 and len(elements) < 2:
                    break
                elem = elements[-1]
            elem.click()
            html = driver.page_source
            self.add_page_to_soup_list(BeautifulSoup(html, 'html.parser'))
        driver.close()
        logging.info('Closed ChromeWebDriver')
        logging.info('Finished populating html pages from courses viewer')

    @classmethod
    def __all_days_valid(cls, days: List[str]):
        for day in days:
            if day.strip("' ") not in Day.single_char_labels():
                return False
        return True

    def __get_chrome_driver(self):
        logging.info(
            'Instantiating ChromeWebDriver object {0} open window'.format('with' if self.open_window else 'without'))
        chrome_driver_location = r'C:\Users\mamalka\PycharmProjects\TelegramBotBIU\3rd_party\chromedriver'
        chrome_options = Options()
        if not self.open_window:
            chrome_options.add_argument('--headless')
        driver_manager = ChromeDriverManager().install()
        driver = webdriver.Chrome(driver_manager, options=chrome_options)
        return driver

    @classmethod
    def parse_location(cls, building_name: str, class_number: str):
        building_number = None
        if '-' in building_name:
            str_list = building_name.split('-')
            building_name = str_list[0].strip()
            building_number = int(str_list[1].strip())
        if class_number.isnumeric():
            class_number = int(class_number)
        return Location.create(building_name=building_name, building_number=building_number, class_number=class_number)

    @classmethod
    def parse_lesson_times(cls, days: List[str], hours: List[str]):
        hours_per_day = int(len(hours) / len(days))
        lesson_time_list = []
        for i, day in enumerate(days):
            day_object = Day.from_string(day.strip("' "))
            for j in range(0, hours_per_day):
                times = hours[i * hours_per_day + j].split(' - ')
                start_time = time.strptime(times[0], cls.time_format)
                end_time = time.strptime(times[1], cls.time_format)
                class_time = LessonTime.create(day=day_object, start_time=start_time, end_time=end_time)
                lesson_time_list.append(class_time)
        return lesson_time_list


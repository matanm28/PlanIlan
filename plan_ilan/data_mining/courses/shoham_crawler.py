import concurrent.futures
import logging
import queue
from logging import Logger
import re
from collections import deque
from datetime import datetime
import threading
from typing import List, Deque, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from django.db import IntegrityError
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.select import Select

from plan_ilan.exceptaions import EnumNotExistError, CantCreateModelError
from plan_ilan.apps.web_site.models import Course, Lesson, Location, DAYS, LessonTime, Teacher, LessonTypeEnum, \
    TitleEnum, \
    DepartmentEnum, SemesterEnum, Exam, ExamPeriodEnum
from plan_ilan.apps.web_site.models import FacultyEnum, Semester, ExamPeriod, Faculty, Title, Department, LessonType, \
    Day
from plan_ilan.utils.general import is_float, is_number

from selenium.common.exceptions import NoSuchElementException, WebDriverException

from plan_ilan.utils.web import get_chrome_driver, close_chrome_driver

DEPARTMENTS_SELECT_PLACE_HOLDER_ID = 'ContentPlaceHolder1_cmbDepartments'
YEAR_SELECT_PLACE_HOLDER_ID = 'ContentPlaceHolder1_cmbYear'
SEARCH_BUTTON_PLACE_HOLDER_ID = 'ContentPlaceHolder1_btnSearch'


class ShohamCrawler:
    def __init__(self, base_url: str, open_window: bool = False, logger: Logger = None):
        self.__logger = logger if logger else logging.getLogger()
        self.logger.info('Creating a ShoamCrawler instance')
        self.__courses_list = []
        self.__num_of_fails = 0
        self.__soups_queue = deque()
        self.__course_detail_url_list = deque()
        self.__base_url = base_url if base_url.endswith('/') else f'{base_url}/'
        self.__open_window = open_window
        self.__running = False
        self.year = None
        self.logger.info('Finished creating a ShoamCrawler instance')

    @property
    def courses_list(self) -> Deque[Course]:
        return self.__courses_list

    @property
    def logger(self):
        return self.__logger

    @property
    def soups_queue(self) -> Deque[BeautifulSoup]:
        return self.__soups_queue

    @property
    def base_url(self) -> str:
        return self.__base_url

    @property
    def open_window(self) -> bool:
        return self.__open_window

    @open_window.setter
    def open_window(self, value: bool):
        self.__open_window = value

    @property
    def course_detail_urls(self) -> Deque:
        return self.__course_detail_url_list

    @property
    def running(self) -> bool:
        return self.__running

    @running.setter
    def running(self, value: bool):
        self.__running = value

    @property
    def num_of_fails(self):
        return self.__num_of_fails

    def start(self, department_name: str = 'בחר', run_with_threads: bool = True):
        self.logger.info(f'Started scraping process {"with threads" if run_with_threads else ""}')
        driver = self.__start_search_and_get_drive(department_name)
        if not run_with_threads:
            self.__run(driver)
        else:
            self.__run_with_threads(driver)
        self.logger.info(f'Finished scraping process total of {len(self.courses_list)} courses processed')

    def __run(self, driver: WebDriver):
        self.parse_pages_to_soup_list(driver)
        self.fill_courses_details_pages_from_courses_table_page()
        q = queue.Queue()
        self.create_courses_from_details_pages(q)
        self.consume_courses_details_pages(q)

    def __start_search_and_get_drive(self, faculty_name: str) -> WebDriver:
        driver = get_chrome_driver(self.open_window)
        driver.get(self.base_url)
        if faculty_name != 'בחר':
            faculty_select = Select(driver.find_element_by_id(DEPARTMENTS_SELECT_PLACE_HOLDER_ID))
            faculty_select.select_by_visible_text(faculty_name)
        year_select = Select(driver.find_element_by_id(YEAR_SELECT_PLACE_HOLDER_ID))
        year_text = year_select.first_selected_option.text.split('-')[1]
        if is_number(year_text):
            self.year = int(year_text)
        else:
            self.logger.error("Can't parse year, correct parse code to continue")
            raise ValueError("Can't parse year, correct parse code to continue")
        driver.find_element_by_id(SEARCH_BUTTON_PLACE_HOLDER_ID).click()
        return driver

    def __run_with_threads(self, driver: WebDriver):
        self.logger.info('Instantiating threads')
        q = queue.Queue()
        threads = [threading.Thread(target=self.create_courses_from_details_pages, args=(q,)),
                   threading.Thread(target=self.consume_courses_details_pages, args=(q,))]
        self.parse_pages_to_soup_list(driver)
        self.running = True
        for thread in threads:
            thread.start()
        threads[0].join()
        self.running = False
        # q.join()
        threads[1].join()
        self.logger.info('All threads finished')

    def parse_pages_to_soup_list(self, driver: WebDriver):
        self.logger.info('Started populating html pages from courses viewer')
        parser = 'html.parser'
        try:
            pagination_tr = driver.find_element_by_css_selector('.cssPager')
            pagination_text = pagination_tr.text
        except NoSuchElementException:
            pagination_text = ''
        pages_numbers = deque(pagination_text.strip('>>').split())
        last_page_number = '0'
        while len(pages_numbers) > 0:
            page_number = pages_numbers.popleft()
            if page_number not in ('1', '...'):
                elements = driver.find_elements_by_link_text(page_number)
                if len(elements) == 1:
                    elements[0].click()
                else:
                    self.logger.error(f'Error on {driver.current_url} with page number {page_number}')
            if page_number == '...':
                elements = driver.find_elements_by_link_text('...')
                if len(elements) == 2:
                    elements[1].click()
                elif len(elements) == 1 and last_page_number == '10':
                    elements[0].click()
                else:
                    continue
                pagination_tr = driver.find_element_by_css_selector('.cssPager')
                pagination_text = pagination_tr.text
                last_page_number = int(last_page_number)
                for item in pagination_text.strip('>> <<').lstrip('...').split():
                    if item == '...' or item.isnumeric() and int(item) > last_page_number:
                        pages_numbers.append(item)
                page_number = pages_numbers.popleft()
            self.soups_queue.append(BeautifulSoup(driver.page_source, parser))
            last_page_number = page_number
        close_chrome_driver(driver)
        self.logger.info('Finished populating html pages from courses viewer')
        self.fill_courses_details_pages_from_courses_table_page()

    def fill_courses_details_pages_from_courses_table_page(self):
        amount_of_urls = 0
        while self.soups_queue:
            soup = self.soups_queue.pop()
            urls = []
            for a in soup.find_all('a', class_='glyphicon'):
                if a.has_attr('href'):
                    urls.append(f'{self.base_url}{a["href"]}')
            self.course_detail_urls.extend(urls)
            amount_of_urls += len(urls)
        self.logger.info(f'Scrapped {amount_of_urls} urls')

    def create_courses_from_details_pages(self, q: queue.Queue):
        driver = get_chrome_driver(self.open_window)
        while self.course_detail_urls:
            url = self.course_detail_urls.popleft()
            try:
                driver.get(url)
                course_details_page = BeautifulSoup(driver.page_source, 'html.parser')
                q.put((course_details_page, url))
            except WebDriverException as e:
                self.logger.exception(e)
                continue
        close_chrome_driver(driver)

    def consume_courses_details_pages(self, products: queue.Queue, num_of_consumers: int = 3):
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_consumers) as executor:
            futures = []
            while self.course_detail_urls or not products.empty():
                builder = CourseInstanceBuilder(self.year, self.base_url, self.logger)
                page, url = products.get()
                args = [builder, page, url]
                futures.append(executor.submit(lambda p: send_data_to_pool_executor(*p), args))
            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    self.logger.exception(future.exception())
                    self.__num_of_fails += 1
                elif future.result() is not None:
                    self.courses_list.append(future.result())
                products.task_done()


def send_data_to_pool_executor(builder: 'CourseInstanceBuilder', page, url):
    return builder.parse_course_details_page(page, url)


class CourseInstanceBuilder:
    __hour_regex = '[0-9][0-9]:[0-9][0-9] - [0-9][0-9]:[0-9][0-9]'
    __time_format = '%d-%m-%Y -- %H:%M'
    BAD_TEACHER_TITLES = ('מרצי מחלקה', 'מחלקה מרצי', '')
    HTML_IDS = {
        'id': re.compile('tdCourseCode', re.IGNORECASE),
        'name': re.compile('pTitle', re.IGNORECASE),
        'department': re.compile('tdDepartment', re.IGNORECASE),
        'faculty': re.compile('tdFaculty', re.IGNORECASE),
        'session_type': re.compile('tdSessionType', re.IGNORECASE),
        'teacher': re.compile('tdTeacher', re.IGNORECASE),
        'semester': re.compile('tdHours', re.IGNORECASE),
        'points': re.compile('tdPoints', re.IGNORECASE),
        'days': re.compile('tdDayOfTheWeek', re.IGNORECASE),
        'session_times': re.compile('tdSessionStartHour', re.IGNORECASE),
        'buildings': re.compile('tdBuilding', re.IGNORECASE),
        'rooms': re.compile('tdRoom', re.IGNORECASE),
        'exams': re.compile('gvTermRooms', re.IGNORECASE),
        'syllabus': re.compile('sylabusHyperLink1', re.IGNORECASE),
    }
    mutex = threading.Lock()

    def __init__(self, courses_year: int, base_url: str, logger) -> None:
        self.year = courses_year
        self.base_url = base_url
        self.logger = logger
        self.all_correct = False

    @classmethod
    def __all_days_valid(cls, days: List[str]):
        for day in days:
            if day.strip("' ") not in DAYS.labels:
                return False
        return True

    @property
    def hour_regex(self):
        return self.__hour_regex

    @property
    def time_format(self) -> str:
        return self.__time_format

    def parse_course_details_page(self, soup: BeautifulSoup, url: str) -> Course:
        self.all_correct = True
        name, session_type = self.__parse_course_name_and_session_type(soup.find(id=self.HTML_IDS['name']),
                                                                       soup.find(id=self.HTML_IDS['session_type']))
        code, group = self.__parse_course_id(soup.find(id=self.HTML_IDS['id']))
        department = self.__parse_course_department(soup.find(id=self.HTML_IDS['department']))
        faculty = self.__parse_course_faculty(soup.find(id=self.HTML_IDS['faculty']))
        teachers = self.__parse_course_teacher(soup.find(id=self.HTML_IDS['teacher']), faculty)
        session_times = self.__parse_course_session_times(soup.find(id=self.HTML_IDS['days']),
                                                          soup.find(id=self.HTML_IDS['session_times']),
                                                          soup.find(id=self.HTML_IDS['semester']))
        points = self.__parse_course_points(soup.find(id=self.HTML_IDS['points']))
        locations = self.__parse_course_locations(soup.find(id=self.HTML_IDS['buildings']),
                                                  soup.find(id=self.HTML_IDS['rooms']))
        syllabus_link = self.__parse_course_syllabus(soup.find(id=self.HTML_IDS['syllabus']))
        course_instance = None
        if self.all_correct:
            exams = self.__parse_course_exams(soup.find(id=self.HTML_IDS['exams']))
            course_instance = Lesson.create(code, group, name, teachers, session_type, faculty, department,
                                            session_times, locations, exams, points, url, syllabus_link)
            self.logger.info(f'Done processing {Lesson.__name__} with code: {course_instance.code},' +
                             f' group: {course_instance.group}, name: {course_instance.name}')
        return course_instance

    def __parse_lesson_times(self, days: List[str], hours: List[str]):
        hours_per_day = int(len(hours) / len(days))
        lesson_time_list = []
        for i, day in enumerate(days):
            day_object = DAYS.from_string(day.strip("'"))
            date = f'{str(18 + day_object.value - 1)}-10-2020 -- '
            for j in range(0, hours_per_day):
                times = hours[i * hours_per_day + j].split(' - ')
                start_time = datetime.strptime(date + times[0], self.time_format)
                end_time = datetime.strptime(date + times[1], self.time_format)
                class_time = LessonTime.create(day=day.strip("'"), start_time=start_time,
                                               end_time=end_time)
                lesson_time_list.append(class_time)
        return lesson_time_list

    def __parse_course_name_and_session_type(self, name_td: Tag, session_type_td: Tag) -> Tuple[str, LessonTypeEnum]:
        if not self.all_correct:
            return
        name, session_type = None, None
        if not name_td or not session_type_td:
            self.all_correct = False
            return name, session_type
        title_list = name_td.text.replace('פרטי קורס', '').strip().split(':', maxsplit=1)
        if title_list:
            name = title_list[-1]
        session_type_str = session_type_td.text.strip()
        if session_type_str == 'תרגיל':
            session_type_str = 'תרגול'
        try:
            session_type_enum = LessonTypeEnum.from_string(session_type_str)
            session_type = LessonType.objects.get(number=session_type_enum.value)
        except EnumNotExistError as err:
            self.logger.warning(f'course: {name}, {err}')
            self.all_correct = False
        return name.strip(), session_type

    def __parse_course_id(self, id_td: Tag) -> Tuple[str, str]:
        if not self.all_correct:
            return None, None
        if not id_td:
            self.all_correct = False
            return None, None
        code, group = None, None
        id_list = id_td.text.strip().split('-')
        if len(id_list) >= 2:
            code, group, *rest = id_list
        else:
            self.all_correct = False
        return code.strip(), group.strip()

    def __parse_course_department(self, department_td: Tag) -> DepartmentEnum:
        if not self.all_correct:
            return None
        if not department_td:
            self.all_correct = False
            return None
        department_str = department_td.text.strip()
        department_enum = DepartmentEnum.from_string(department_str)
        return Department.objects.get(number=department_enum)

    def __parse_course_faculty(self, faculty_td: Tag) -> str:
        if not self.all_correct:
            return ''
        faculty_enum = FacultyEnum.from_string(faculty_td.text.strip()) if faculty_td else FacultyEnum.UNKNOWN
        return Faculty.objects.get(number=faculty_enum.value)

    def __parse_course_teacher(self, teacher_td: Tag, faculty: Faculty) -> List[Teacher]:
        if not self.all_correct:
            return []
        if not teacher_td:
            self.all_correct = False
            return []
        teachers_list = []
        for name in teacher_td.contents:
            if not isinstance(name, NavigableString):
                continue
            if name in self.BAD_TEACHER_TITLES:
                continue
            title_string, full_name = name.strip().split(maxsplit=1)
            try:
                title_enum = TitleEnum.from_string(title_string.strip("'"))
            except EnumNotExistError:
                full_name = f'{title_string} {full_name}'
                title_enum = TitleEnum.BLANK
            try:
                title = Title.objects.get(number=title_enum)
                teacher = Teacher.create(title=title, name=full_name.strip(), faculty=faculty)
                teachers_list.append(teacher)
            except (EnumNotExistError, CantCreateModelError) as err:
                self.logger.exception(err)
            except IntegrityError as err:
                self.logger.exception(err)
        if not teachers_list:
            self.all_correct = False
        return teachers_list

    def __parse_course_semester(self, semester_td: Tag) -> Semester:
        if not self.all_correct:
            return None
        semesters = [semester_name.split('-')[0].strip(" '") for semester_name in semester_td.text.strip().split('\n')]
        semester = None
        try:
            if len(semesters) == 1:
                semester = SemesterEnum.from_string(semesters[0])
            elif len(semesters) == 2:
                if SemesterEnum.FIRST.label and SemesterEnum.SECOND.label in semesters:
                    semester = SemesterEnum.YEARLY
            else:
                self.all_correct = False
        except EnumNotExistError as err:
            self.logger.warning(f'{err}')
            self.all_correct = False
        return Semester.objects.get(number=semester.value) if self.all_correct else None

    def __parse_course_session_times(self, days_td: Tag, session_times_td: Tag, semester_td: Tag) -> List[LessonTime]:
        if not self.all_correct:
            return []
        if not semester_td or not days_td or not session_times_td:
            self.all_correct = False
            return []
        semester = self.__parse_course_semester(semester_td)
        if not self.all_correct:
            return []
        day_chars_list = [day_char.strip("'") for day_char in days_td.text.strip().split(',')]
        session_times_list = re.findall(self.hour_regex, session_times_td.text.strip())
        if semester.number == SemesterEnum.YEARLY and len(session_times_list) == 2:
            if session_times_list[0].strip() == session_times_list[1].strip():
                session_times_list.pop(1)
        if len(session_times_list) != len(day_chars_list):
            self.all_correct = False
            return []
        session_start_and_end_times = [session_time.strip().split('-') for session_time in
                                       session_times_list]
        session_times = []
        for (start_time_str, end_time_str), day_char in zip(session_start_and_end_times, day_chars_list):
            date = '18-10-2020 -- '
            start_time = datetime.strptime(date + start_time_str.strip(), self.time_format)
            end_time = datetime.strptime(date + end_time_str.strip(), self.time_format)
            day_enum = DAYS.from_string(day_char)
            day = Day.objects.get(number=day_enum)
            session_time = LessonTime.create_thread_safe(semester=semester, day=day, start_time=start_time,
                                                         end_time=end_time,
                                                         year=self.year)
            session_times.append(session_time)
        if not session_times:
            self.all_correct = False
        return session_times

    def __parse_course_locations(self, buildings_td: Tag, rooms_td: Tag) -> List[Location]:
        if not self.all_correct:
            return []
        if not buildings_td or not rooms_td:
            # self.all_correct = False
            return []
        buildings_list = []
        room_numbers_list = []
        if buildings_td.table.tbody:
            for tr in buildings_td.table.tbody:
                buildings_list.append(tr.text)
        if rooms_td.table.tbody:
            for tr in rooms_td.table.tbody:
                room_numbers_list.append(tr.text)
        if len(buildings_list) > len(room_numbers_list) > 0:
            for i in range(len(buildings_list) - len(room_numbers_list)):
                room_numbers_list.append(room_numbers_list[i])
        locations_list = []
        for building, room_number in zip(buildings_list, room_numbers_list):
            locations_list.append(self.__parse_single_location(building, room_number))
        if not locations_list:
            self.all_correct = False
        return locations_list

    def __parse_single_location(self, building_name: str, class_number: str) -> Location:
        building_number = None
        if '-' in building_name:
            str_list = building_name.split('-')
            building_name = str_list[0].strip()
            building_number = int(str_list[1].strip())
        if class_number.isnumeric():
            class_number = int(class_number)
        else:
            class_number = None
        online = building_name in ('נלמד בזום', 'טרם שובץ')
        return Location.create_thread_safe(building_name=building_name, building_number=building_number,
                                           class_number=class_number,
                                           online=online)

    def __parse_course_points(self, points_td: Tag) -> float:
        if not self.all_correct:
            return None
        return float(points_td.text.strip()) if is_float(points_td.text.strip()) else None

    def __parse_course_exams(self, exam_table: Tag) -> List[Exam]:
        if not self.all_correct:
            return []
        if not exam_table:
            return []
        exam_tuple_list = []
        for tr in exam_table.tbody.find_all('tr'):
            line_data = []
            for td in tr.find_all('td')[:3]:
                data = td.text.strip('\n ')
                if data:
                    line_data.append(data)
            if len(line_data) != 3:
                continue
            exam_tuple_list.append(tuple(line_data))
        exams_list = []
        # *rest is used to collect irrelevant data that can appear sometimes
        for period, date, time_str, *rest in exam_tuple_list:
            try:
                date_time_data = datetime.strptime(f'{date} {time_str}', '%d/%m/%Y %H:%M')
                period_enum = ExamPeriodEnum.from_string(period)
                exams_list.append(
                    Exam.create(period=ExamPeriod.objects.get(number=period_enum.value), date=date_time_data))
            except EnumNotExistError as err:
                self.logger.warning(f'{err}')
                self.all_correct = False
            except Exception as e:
                raise e
        return exams_list

    def __parse_course_syllabus(self, syllabus_anchor: Tag) -> str:
        if not self.all_correct:
            return ''
        syllabus_link = None
        if syllabus_anchor and syllabus_anchor.has_attr('href'):
            syllabus_link = f'{self.base_url}{syllabus_anchor["href"]}'
        return syllabus_link

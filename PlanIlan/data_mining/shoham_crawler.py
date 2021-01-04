import logging
import time
import re
from collections import deque
from datetime import datetime
from typing import List, Deque, Tuple

from bs4 import BeautifulSoup, Tag

from PlanIlan.exceptaions import EnumNotExistError, CantCreateModelError
from PlanIlan.models import Course, Location, Day, SessionTime, Teacher, SessionType, TeacherTitle, Department, \
    Semester, Exam, ExamPeriod
from PlanIlan.utils.general import name_of

from selenium.common.exceptions import NoSuchElementException

from PlanIlan.utils.web import get_chrome_driver, close_chrome_driver

BUILDING_PLACE_HOLDER_ID = 'ContentPlaceHolder1_tdBuilding'
ROOM_PLACE_HOLDER_ID = 'ContentPlaceHolder1_tdRoom'


class ShohamCrawler:
    __hour_regex = '[0-9][0-9]:[0-9][0-9] - [0-9][0-9]:[0-9][0-9]'
    __time_format = '%d-%m-%Y -- %H:%M'
    BAD_TEACHER_TITLES = ('מרצי מחלקה', 'מחלקה מרצי')

    def __init__(self, base_url: str):
        logging.info('Creating a ShoamCrawler instance')
        self.__courses_list = []
        self.__teachers_list = []
        self.__html_links = deque
        self.__soups_list = deque()
        self.__course_detail_url_list = deque()
        self.__base_url = base_url if base_url.endswith('\\') else f'{base_url}\\'
        self.__print_soup = False
        self.__open_window = False
        self.__running = False
        self.__all_correct = False
        logging.info('Finished creating a ShoamCrawler instance')

    @property
    def courses_list(self) -> Deque[Course]:
        return self.__courses_list

    @property
    def html_links(self) -> Deque[str]:
        return self.__html_links

    @property
    def soups_list(self) -> Deque[BeautifulSoup]:
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
    def time_format(self) -> str:
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

    @property
    def course_detail_urls(self):
        return self.__course_detail_url_list

    @property
    def running(self) -> bool:
        return self.__running

    @running.setter
    def running(self, value: bool):
        self.__running = value

    @property
    def all_correct(self) -> bool:
        return self.__all_correct

    @all_correct.setter
    def all_correct(self, value: bool):
        self.__all_correct = value

    def add_html_page(self, link: str):
        self.html_links.append(link)

    def add_page_to_soup_list(self, content: BeautifulSoup):
        self.soups_list.append(content)

    def parse_single_course_page(self, soup: BeautifulSoup) -> List[Course]:
        page_courses_list = []
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
            session_type = tr.contents[5].text.strip()
            if not session_type or session_type not in SessionType.labels:
                continue
            teacher_data = tr.contents[4].text.strip()
            if not teacher_data and teacher_data not in ShohamCrawler.BAD_TEACHER_TITLES:
                continue
            teacher_title, teacher_name = teacher_data.split(' ', 1)
            if not teacher_name or not teacher_title:
                continue
            if teacher_title not in TeacherTitle.labels:
                teacher_name = teacher_data
                teacher_title = ''
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
            link = f"{self.base_url}{tr.contents[9].find('a', href=True)['href']}"
            teacher = Teacher.create(teacher_name, teacher_title.strip("' "))
            course_dict = {'id': id, 'name': course_name, 'teacher': teacher, 'lesson_times': lesson_time_list,
                           'semester': semester, 'link': link}
            page_courses_list.append(course_dict)
        return page_courses_list

    def parse_all_content(self):
        driver = get_chrome_driver(self.open_window)
        for page in self.soups_list:
            page_courses = self.parse_single_course_page(page)
            for course_dict in page_courses:
                driver.get(course_dict['link'])
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                buildings_list = []
                room_numbers_list = []
                if soup.find(id=BUILDING_PLACE_HOLDER_ID).table.tbody:
                    for tr in soup.find(id=BUILDING_PLACE_HOLDER_ID).table.tbody:
                        buildings_list.append(tr.text)
                if soup.find(id=ROOM_PLACE_HOLDER_ID).table.tbody:
                    for tr in soup.find(id=ROOM_PLACE_HOLDER_ID).table.tbody:
                        room_numbers_list.append(tr.text)
                locations_list = ShohamCrawler.parse_locations(buildings_list, room_numbers_list)
                course = Course.create(course_dict['id'], course_dict['name'], course_dict['teacher'],
                                       course_dict['lesson_times'], locations_list, course_dict['semester'],
                                       course_dict['link'])
                logging.info(
                    f'Done processing course with code:{course.code}, group:{course.group_code}, '
                    f'name:{course.name}')
                self.courses_list.append(course)
        driver.close()
        logging.info('Closed ChromeWebDriver')

    def populate_html_pages_from_course_viewer(self, faculty_name: str = 'בחר'):
        logging.info('Started populating html pages from courses viewer')
        driver = get_chrome_driver(self.open_window)
        driver.get(self.base_url)
        search = '//*[@id="ContentPlaceHolder1_btnSearch"]'
        if faculty_name != 'בחר':
            faculty_place_holder = '//*[@id="ContentPlaceHolder1_cmbDepartments"]'
            driver.find_element_by_xpath(faculty_place_holder).send_keys(faculty_name)
        driver.find_element_by_xpath(search).click()
        html = driver.page_source
        self.add_page_to_soup_list(BeautifulSoup(html, 'html.parser'))
        # todo change to while loop
        for i in range(2, 499):
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
        close_chrome_driver(driver)
        logging.info('Finished populating html pages from courses viewer')

    def fill_courses_details_pages_from_courses_table_page(self):
        driver = get_chrome_driver(self.open_window)
        consecutive_times_slept = 0
        while self.running:
            if consecutive_times_slept > 5:
                logging.info(
                    f'function {name_of(self.fill_courses_details_pages_from_courses_table_page)} sleeping for to many cycles...breaking')
                break
            if not self.soups_list:
                logging.info(
                    f'function {name_of(self.fill_courses_details_pages_from_courses_table_page)} going to sleep for 2 seconds')
                time.sleep(2)
                consecutive_times_slept += 1
                continue
            soup = self.soups_list.pop()
            urls = []
            for a in soup.find_all('a', class_='glyphicon'):
                urls.append(f'{self.base_url}{a.href}')
            self.course_detail_urls.extend(urls)
            consecutive_times_slept = 0
        close_chrome_driver(driver)

    def create_courses_from_details_pages(self):
        driver = get_chrome_driver(self.open_window)
        courses_list = []
        while self.running:
            if not self.course_detail_urls:
                time.sleep(2)
                continue
            url = self.course_detail_urls.popleft()
            driver.get(url)
            course_details_page = BeautifulSoup(driver.page_source, 'html.parser')
            course = self.parse_course_details_page(course_details_page)
            if self.all_correct:
                courses_list.append(course)

    @classmethod
    def __all_days_valid(cls, days: List[str]):
        for day in days:
            if day.strip("' ") not in Day.labels:
                return False
        return True

    def parse_lesson_times(self, days: List[str], hours: List[str]):
        hours_per_day = int(len(hours) / len(days))
        lesson_time_list = []
        for i, day in enumerate(days):
            day_object = Day.from_string(day.strip("'"))
            date = f'{str(18 + day_object.value - 1)}-10-2020 -- '
            for j in range(0, hours_per_day):
                times = hours[i * hours_per_day + j].split(' - ')
                start_time = datetime.strptime(date + times[0], self.time_format)
                end_time = datetime.strptime(date + times[1], self.time_format)
                class_time = SessionTime.create_without_save(day=day.strip("'"), start_time=start_time,
                                                             end_time=end_time)
                lesson_time_list.append(class_time)
        return lesson_time_list

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

    def parse_course_details_page(self, soup: BeautifulSoup) -> Course:
        self.all_correct = True
        name, session_type = self.parse_course_name_and_session_type(soup.find(id=self.HTML_IDS['name']),
                                                                     soup.find(id=self.HTML_IDS['session_type']))
        code, group = self.parse_course_id(soup.find(id=self.HTML_IDS['id']))
        department = self.parse_course_department(soup.find(id=self.HTML_IDS['department']))
        faculty = self.parse_course_faculty(soup.find(id=self.HTML_IDS['faculty']))
        teachers = self.parse_course_teacher(soup.find(id=self.HTML_IDS['teacher']))
        session_times = self.parse_course_session_times(soup.find(id=self.HTML_IDS['days']),
                                                        soup.find(id=self.HTML_IDS['session_times']),
                                                        soup.find(id=self.HTML_IDS['semester']))
        points = self.parse_course_points(soup.find(id=self.HTML_IDS['points']))
        locations = self.parse_course_locations(soup.find(id=self.HTML_IDS['buildings']),
                                                soup.find(id=self.HTML_IDS['rooms']))
        exams = self.parse_course_exams(soup.find(id=self.HTML_IDS['exams']))
        syllabus_link = self.parse_course_syllabus(soup.find(id=self.HTML_IDS['syllabus']))
        course = None
        if self.all_correct:
            course = Course.create()
        return course

    def parse_course_name_and_session_type(self, name_td: Tag, session_type_td: Tag) -> Tuple[str, SessionType]:
        session_type, name = None, None
        title_list = name_td.text.replace('פרטי קורס :', '').strip().split(':')
        if title_list:
            name = title_list[-1]
        session_type_str = session_type_td.text.strip()
        try:
            session_type = SessionType.from_string(session_type_str)
        except EnumNotExistError as err:
            logging.error(f'{err}')
            self.all_correct = False
        return name, session_type

    def parse_course_id(self, id_td: Tag) -> Tuple[str, str]:
        code, group = None, None
        id_list = id_td.text.strip().split('-')
        if len(id_list) >= 2:
            code, group, *rest = id_list
        else:
            self.all_correct = False
        return code, group

    def parse_course_department(self, department_td: Tag) -> Department:
        department = None
        department_str = department_td.text.strip()
        try:
            department = Department.from_string(department_str)
        except EnumNotExistError as err:
            logging.error(f'{err}')
            self.all_correct = False
        return department

    def parse_course_faculty(self, faculty_td: Tag) -> str:
        return faculty_td.text.strip()

    def parse_course_teacher(self, teacher_td: Tag) -> List[Teacher]:
        teacher_names = teacher_td.text.split('\n')
        teachers_list = []
        for name in teacher_names:
            title, *full_name = name.strip().split()
            full_name = ' '.join(full_name)
            try:
                teacher = Teacher.create(title=title, name=full_name)
                teachers_list.append(teacher)
            except (EnumNotExistError, CantCreateModelError) as err:
                logging.error(f'{err}')
        if not teachers_list:
            self.all_correct = False
        return teachers_list

    def parse_course_semester(self, semester_td: Tag) -> Semester:
        semesters = [semester_name.split('-')[0].strip(" '") for semester_name in semester_td.text.strip().split('\n')]
        semester = None
        try:
            if len(semesters) == 1:
                semester = Semester.from_string(semesters[0])
            elif len(semesters) == 2:
                if Semester.FIRST.label and Semester.SECOND.label in semesters:
                    semester = Semester.YEARLY
            else:
                semester = None
                self.all_correct = False
        except EnumNotExistError as err:
            logging.error(f'{err}')
            self.all_correct = False
        return semester

    def parse_course_session_times(self, days_td: Tag, session_times_td: Tag, semester_td: Tag) -> List[SessionTime]:
        semester = self.parse_course_semester(semester_td)
        if not self.all_correct:
            return []
        day_chars_list = days_td.text.strip().split(',')
        session_times_list = session_times_td.text.strip().split('\n')
        if semester == semester.YEARLY and len(session_times_list) == 2:
            if session_times_list[0].strip() == session_times_list[1].strip():
                session_times_list.pop(1)
        if len(session_times_list) != len(day_chars_list):
            self.all_correct = False
            return []
        session_start_and_end_times = [session_time.split('-') for session_time in session_times_list]
        session_times = []
        for (start_time_str, end_time_str), day in zip(session_start_and_end_times, day_chars_list):
            date = '18-10-2020 -- '
            start_time = datetime.strptime(date + start_time_str, self.time_format)
            end_time = datetime.strptime(date + end_time_str, self.time_format)
            session_time = SessionTime.create(semester=semester, day=day, start_time=start_time, end_time=end_time)
            session_times.append(session_time)
        if not session_times:
            self.all_correct = False
        return session_times

    def parse_course_locations(self, buildings_td: Tag, rooms_td: Tag) -> List[Location]:
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
            locations_list.append(ShohamCrawler.parse_single_location(building, room_number))
        if not locations_list:
            self.all_correct = False
        return locations_list

    def parse_single_location(self, building_name: str, class_number: str) -> Location:
        # todo return as list
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
        return Location.create_without_save(building_name=building_name, building_number=building_number,
                                            class_number=class_number,
                                            online=online)

    def parse_course_points(self, points_td: Tag) -> float:
        return int(points_td.text.strip()) if points_td.text.isnumeric() else None

    def parse_course_exams(self, exam_table: Tag) -> List[Exam]:
        if not exam_table:
            return []
        exam_tuple_list = []
        for tr in exam_table.tbody.findall('tr'):
            line_data = []
            for td in tr.findall('td'):
                data = td.text.strip('\n ')
                if data:
                    line_data.append(data)
            exam_tuple_list.append(tuple(line_data))
        exams_list = []
        for period, date, time_str in exam_tuple_list:
            try:
                date_time_data = datetime.strptime(f'{date} {time_str}', '%d/%m/%Y %H:%M')
                period_enum = ExamPeriod.from_string(period)
                exams_list.append(Exam.create_without_save(period=period_enum, date=date_time_data))
            except EnumNotExistError as err:
                logging.error(f'{err}')
                self.all_correct = False
            finally:
                return exams_list

    def parse_course_syllabus(self, syllabus_anchor: Tag) -> str:
        syllabus_link = None
        if syllabus_anchor and syllabus_anchor.has_attr('href'):
            syllabus_link = f'{self.base_url}{syllabus_anchor["href"]}'
        return syllabus_link

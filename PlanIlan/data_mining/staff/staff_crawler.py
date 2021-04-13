from typing import Dict, List, Union, Tuple
from urllib.parse import urljoin

import requests
from PIL import Image
from bs4 import BeautifulSoup
from email_validator import validate_email, EmailNotValidError

from PlanIlan.data_mining.staff.lookup_parameters import StaffLookup
from PlanIlan.models.enums import FacultyEnum, DepartmentEnum


class StaffCrawler:
    """An object that crawls over different staff members web pages according to their attributes."""

    def __init__(self, url: Union[str, List[str]], faculty: FacultyEnum, department: DepartmentEnum, staff_lookup: StaffLookup,
                 **kwargs) -> None:
        self._urls = url if isinstance(url, List) else [url]
        self._faculty = faculty
        self._department = department
        self.staff_lookup = staff_lookup
        self._has_photos = kwargs['has_photos'] if 'has_photos' in kwargs else True
        self._email_suffix = kwargs['email_suffix'] if 'email_suffix' in kwargs else ''
        self.__teachers_data = None

    @property
    def urls(self) -> List[str]:
        """Return the url of the crawled web page"""
        return self._urls

    @property
    def faculty(self) -> FacultyEnum:
        """Return the faculty of the crawled web page"""
        return self._faculty

    @property
    def department(self):
        """Returns the department of the crawled web page"""
        return self._department

    def get_teachers_data(self) -> List[Dict]:
        if self.__teachers_data is None:
            self.crawl()
        return self.__teachers_data

    def crawl(self) -> List[Dict]:
        """"The main method for this interface, crawls over the staff members web page an return the data found."""
        self.__teachers_data = []
        for url in self.urls:
            response = requests.get(url)
            if not response:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            persons = self.staff_lookup.persons.get_tags(soup)
            for person in persons:
                teacher_data = {}
                details_url = self.staff_lookup.details_url.get_single_tag(person)
                if details_url is None:
                    continue
                details_url = details_url['href'].strip()
                title = self.staff_lookup.params.title.get_values_from_tag(person)
                name = self.staff_lookup.params.name.get_values_from_tag(person)
                if title is None or name is None:
                    continue
                teacher_data['title'] = title
                teacher_data['name'] = name
                teacher_response = requests.get(details_url)
                if not teacher_response:
                    continue
                teacher_web_page = BeautifulSoup(teacher_response.text, 'html.parser')
                email = self.staff_lookup.params.email.get_values_from_tag(teacher_web_page)
                if not email:
                    email = ''
                mail_valid, value = self._validate_email(email)
                if mail_valid:
                    email = value
                else:
                    # todo: add logging
                    print(email, value)
                phone = self.staff_lookup.params.phone.get_values_from_tag(teacher_web_page)
                website = self.staff_lookup.params.website.get_values_from_tag(teacher_web_page)
                office = self.staff_lookup.params.office.get_values_from_tag(teacher_web_page)
                image_tag = self.staff_lookup.params.photo.get_single_tag(teacher_web_page)
                image_url = urljoin(url, image_tag['src'])
                photo = Image.open(requests.get(image_url, stream=True).raw)
                photo.save(fr'images\img1.jpg')

                teacher_data['email'] = email
                teacher_data['phone'] = phone if phone else ''
                teacher_data['website'] = website if website else ''
                teacher_data['office'] = office if office else ''
                teacher_data['photo'] = photo
                self.__teachers_data.append(teacher_data)
        return len(self.__teachers_data)

    def _validate_email(self, email: str) -> Tuple[bool, Union[Dict, str]]:
        """Validate the given email address
        Args:
            email:str
                The email to validate
        Returns:
            tuple -
                A tuple of size 2:
                1) outcome - indicates whether the email address is valid
                2) value - if outcome is true returns the email address in normalized form, else
                           returns a human readable error message.
        """
        try:
            if '@' not in email:
                email = f'{email}{self._email_suffix}'
            valid = validate_email(email, timeout=10)
            outcome = True
            value = valid.email
        except EmailNotValidError as e:
            outcome = False
            value = str(e)
        return outcome, value

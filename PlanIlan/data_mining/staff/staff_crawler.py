from typing import Dict, List, Union, Tuple
from urllib.parse import urljoin

import requests
from PIL import Image
from bs4 import BeautifulSoup
from email_validator import validate_email, EmailNotValidError

from PlanIlan.models.enums import Faculty, Department


class StaffCrawler:
    """An interface that crawls over different staff members web pages according to their attributes."""

    def __init__(self, url: Union[str, List[str]], faculty: Faculty, department: Department, items_class: str,
                 key_to_class: Dict, **kwargs) -> None:
        self._urls = url if isinstance(url, List) else [url]
        self._faculty = faculty
        self._department = department
        self._items_class = items_class
        self._has_photos = kwargs['has_photos'] if 'has_photos' in kwargs else False
        self._email_suffix = kwargs['email_suffix'] if 'email_suffix' in kwargs else None
        if not all(k in ['photo', 'title', 'name', 'office', 'phone', 'email', 'website'] for k in key_to_class):
            raise ValueError(f"every key in key_to_class must be in "
                             f"{['photo', 'title', 'name', 'office', 'phone', 'email', 'website']}")
        self._key_to_class = key_to_class

    @property
    def urls(self) -> List[str]:
        """Return the url of the crawled web page"""
        return self._urls

    @property
    def faculty(self) -> Faculty:
        """Return the faculty of the crawled web page"""
        return self._faculty

    @property
    def department(self):
        """Returns the department of the crawled web page"""
        return self._department

    @property
    def key_to_data(self):
        return self._key_to_class

    @property
    def items_class(self):
        return self._items_class

    def crawl(self) -> List[Dict]:
        """"The main method for this interface, crawls over the staff members web page an return the data found."""
        teachers_data = []
        for url in self.urls:
            response = requests.get(url)
            if not response:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.select(f'.{self._items_class}'):
                item_data = {}
                for key, value in self.key_to_data.items():
                    if key == "photo" and self._has_photos:
                        image_tag = item.find(class_=value).find('img')
                        img_url = urljoin(url, image_tag['src'])
                        img = Image.open(requests.get(img_url, stream=True).raw)
                        # img.save(fr'images\img1.jpg')
                        item_data[key] = img
                    else:
                        tag = item.find(class_=value)
                        data = tag.text
                        item_data[key] = data
                teachers_data.append(item_data)
        return teachers_data

    def _add_email_suffix_to_mail(self, email: str):
        if '@' not in email and self._email_suffix is not None:
            return email.strip() + self._email_suffix
        return email.strip()

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
            valid = validate_email(email, timeout=10)
            outcome = True
            value = valid.email
        except EmailNotValidError as e:
            outcome = False
            value = str(e)
        return outcome, value

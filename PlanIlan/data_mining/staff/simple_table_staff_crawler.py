from typing import List, Dict, Tuple, Union

import requests
from PIL.Image import Image
from bs4 import BeautifulSoup
from email_validator import validate_email, EmailNotValidError

from PlanIlan.data_mining.staff.staff_crawler import StaffCrawler
from PlanIlan.models import Department
from PlanIlan.models.enums import Faculty


class SimpleTableStaffCrawler(StaffCrawler):
    def __init__(self, url: str, faculty: Faculty, department: Department, key_to_class: Dict, email_suffix: str = None,
                 has_photos: bool = True) -> None:
        super().__init__(url, faculty, department, key_to_class)
        self._email_suffix = email_suffix
        self._has_photos = has_photos

    def crawl(self) -> List[Dict]:
        teachers_data = []
        for url in self.urls:
            response = requests.get(url)
            if not response:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            for table in soup.select(".views_table"):
                for key,value in self.key_to_data.items():
                    if key == "photo" and self._has_photos:
                        img_url = table.find
                        img = Image.open(requests.get())

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

import abc
from typing import List

from PIL.Image import Image
from bs4 import Tag

from .lookup_parameters import StaffLookupAnswer


class StaffParser(metaclass=abc.ABCMeta):
    def __init__(self, answer: StaffLookupAnswer) -> None:
        self._answer = answer

    def set_answer(self, answer: StaffLookupAnswer) -> None:
        if answer:
            self._answer = answer

    def get_name(self) -> str:
        if isinstance(self._answer.name, str):
            return self._answer.name
        return self._parse_name()

    @abc.abstractmethod
    def _parse_name(self):
        """makes a more complicated and specific parsing of the name value from the StaffLookupAnswer"""
        raise NotImplementedError

    def get_title(self) -> str:
        if isinstance(self._answer.title, str):
            return self._answer.title
        return self._parse_title()

    @abc.abstractmethod
    def _parse_title(self):
        """makes a more complicated and specific parsing of the title value from the StaffLookupAnswer"""
        raise NotImplementedError

    def get_email(self) -> str:
        if isinstance(self._answer.email, str):
            return self._answer.email
        return self._parse_email()

    @abc.abstractmethod
    def _parse_email(self):
        """makes a more complicated and specific parsing of the email value from the StaffLookupAnswer"""
        raise NotImplementedError

    def get_phone(self) -> str:
        if isinstance(self._answer.phone, str):
            return self._answer.phone
        return self._parse_phone()

    @abc.abstractmethod
    def _parse_phone(self):
        """makes a more complicated and specific parsing of the phone value from the StaffLookupAnswer"""
        raise NotImplementedError

    def get_photo(self) -> Image:
        return self._answer.photo

    def get_office(self) -> str:
        if isinstance(self._answer.office, str):
            return self._answer.office
        return self._parse_office()

    @abc.abstractmethod
    def _parse_office(self):
        """makes a more complicated and specific parsing of the office value from the StaffLookupAnswer"""
        raise NotImplementedError

    def get_website(self) -> str:
        if isinstance(self._answer.website, str):
            return self._answer.website
        return self._parse_website()

    @abc.abstractmethod
    def _parse_website(self):
        """makes a more complicated and specific parsing of the website value from the StaffLookupAnswer"""
        raise NotImplementedError


class StaffParserBase(StaffParser):
    def __init__(self, answer: StaffLookupAnswer, with_class: str = '') -> None:
        super().__init__(answer)
        self._with_class = with_class

    def _parse_tags_to_str_list(self, tags: List[Tag], unique: bool = True) -> List[str]:
        str_list = []
        for tag in tags:
            if self._with_class in tag.get('class'):
                str_list.append(list(tag.stripped_strings))
        return list(set(str_list)) if unique else str_list

    def _parse_name(self) -> str:
        return ' '.join(self._parse_tags_to_str_list(self._answer.name))

    def _parse_title(self) -> str:
        return ' '.join(self._parse_tags_to_str_list(self._answer.title))

    def _parse_email(self) -> str:
        return ' '.join(self._parse_tags_to_str_list(self._answer.email))

    def _parse_phone(self) -> str:
        return ' '.join(self._parse_tags_to_str_list(self._answer.phone))

    def _parse_office(self) -> str:
        return ' '.join(self._parse_tags_to_str_list(self._answer.name))

    def _parse_website(self) -> str:
        return ' '.join(self._parse_tags_to_str_list(self._answer.name))


class FieldItemStaffParser(StaffParserBase):
    def __init__(self, answer: StaffLookupAnswer) -> None:
        super().__init__(answer, 'field__item')

import dataclasses
import re
from dataclasses import dataclass, field
from enum import Enum, unique, auto
from typing import Union, List, Dict, ClassVar, Set

from PIL.Image import Image
from bs4.element import Tag

from PlanIlan.utils.general import name_of

JOINT_SEPARATOR = '@'


def construct_lookup(v: Union[Dict, str]):
    if not isinstance(v, (Dict, str)):
        raise ValueError(f'{name_of(v)} must be of type {(Dict, str)}')
    if isinstance(v, Dict):
        if 'key' not in v:
            raise ValueError('Lookup dict must contain "key" entry')
        key = v['key']
        selector = SelectorMethod.get_selector_type_by_name(v['selector']) if 'selector' in v else SelectorMethod.FIND
    else:
        key = v
        selector = SelectorMethod.FIND
    return Lookup(key=key, selector_method=selector)


@unique
class SelectorMethod(Enum):
    FIND = auto()
    SELECT = auto()

    @classmethod
    def get_selector_type_by_name(cls, name: str) -> 'SelectorMethod':
        return cls.__members__[name.upper()]

    @property
    def selector_prefix(self) -> str:
        selector = ''
        if self == SelectorMethod.FIND:
            selector = '.'
        elif self == SelectorMethod.SELECT:
            selector = '#'
        return selector


@dataclass(unsafe_hash=True)
class Lookup:
    key: str
    _selector_method: SelectorMethod = field(init=False)
    __regex: re.Pattern = field(init=False, compare=False, default=None)
    __tags: Set[str] = field(init=False, compare=False, default_factory=set)
    separators: ClassVar[List[str]] = [',', '|']
    css_selectors: ClassVar[List[str]] = ['>', '<', ':', ' ']

    def __post_init__(self) -> None:
        if self.key is None:
            return
        # cleans key from multi-spaces and trims start and end
        self.key = ' '.join(self.key.split())
        css_selector_flag = False
        if self.key.startswith('.'):
            css_selector_flag = True
        for selector in self.css_selectors:
            if selector not in self.key:
                continue
            if selector == ' ' and self.key.count(',') == self.key.count(selector):
                continue
            css_selector_flag = True
            break
        if css_selector_flag:
            self._selector_method = SelectorMethod.SELECT
            return
        self._selector_method = SelectorMethod.FIND
        pattern = self.key
        if any(sep in self.key for sep in self.separators):
            translation = str.maketrans({sep: JOINT_SEPARATOR for sep in self.separators})
            keys_list = self.key.translate(translation).split(JOINT_SEPARATOR)
            class_patterns = []
            for key in keys_list:
                if not key:
                    continue
                if '.' in key:
                    tag, c = key.strip().split('.')
                    class_patterns.append(c)
                    self.__tags.add(tag)
                else:
                    class_patterns.append(key)
            pattern = '|'.join(class_patterns)
        self.__regex = re.compile(pattern)

    @property
    def is_valid(self) -> bool:
        return True if self.key else False

    def __bool__(self):
        return self.is_valid

    def get_tags(self, web_element: Tag) -> List[Tag]:
        if self._selector_method == SelectorMethod.SELECT:
            tags = web_element.select(self.key)
        else:
            if self.__regex is not None:
                tags = web_element.find_all(self.__tags, class_=self.__regex)
            else:
                tags = web_element.find_all(self.__tags)
        return tags

    def get_single_tag(self, web_element) -> Tag:
        if self._selector_method == SelectorMethod.SELECT:
            tag = web_element.select_one(self.key)
        else:
            if self.__regex is not None:
                tag = web_element.find(self.__tags, class_=self.__regex)
            else:
                tag = web_element.find(self.__tags)
        return tag

    def get_values_from_tag(self, web_element: Tag) -> Union[str, List[str]]:
        tags = self.get_tags(web_element)
        if not tags:
            ret = []
        elif len(tags) == 1:
            ret = list(tags[0].stripped_strings)
            if len(ret) <= 1:
                ret = ''.join(ret)
        else:
            if any('field__item' in tag.get('class') for tag in tags):
                pass
            ret = set()
            for tag in tags:
                if 'field__item' in tag.get('class'):
                    ret = ''.join(list(tag.stripped_strings))
                    break
                ret.update(list(tag.stripped_strings))
            if isinstance(ret, Set):
                ret = list(ret)
        return ret


@dataclass
class LookupParameters:
    name: Lookup
    title: Lookup
    email: Lookup
    phone: Lookup
    photo: Lookup
    office: Lookup
    website: Lookup

    @classmethod
    def from_dict(cls, d: Dict) -> 'LookupParameters':
        fields = [f.name for f in dataclasses.fields(cls)]
        if not all([str(k).lower() in fields for k in d.keys()]):
            return None
        name = construct_lookup(d['name'])
        title = construct_lookup(d['title'])
        email = construct_lookup(d['email'])
        phone = construct_lookup(d['phone'])
        photo = construct_lookup(d['photo']) if 'photo' in d else Lookup()
        office = construct_lookup(d['office']) if 'office' in d else Lookup()
        website = construct_lookup(d['website']) if 'website' in d else Lookup()
        return LookupParameters(name=name, title=title, email=email,
                                phone=phone, photo=photo, office=office, website=website)


@dataclass
class StaffLookupAnswer:
    _name: str = field(default='')
    _title: str = field(default='')
    _email: Union[str, List[Tag]] = field(default='')
    _phone: Union[str, List[Tag]] = field(default='')
    _photo: Image = field(default=None)
    _office: Union[str, List[Tag]] = field(default='')
    _website: Union[str, List[Tag]] = field(default='')

    @property
    def is_valid(self) -> bool:
        return True if self.name and self.title else False

    def __bool__(self) -> bool:
        return self.is_valid

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value if value else ''

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value if value else ''

    @property
    def email(self) -> Union[str, List[Tag]]:
        return self._email

    @email.setter
    def email(self, value: Union[str, List[Tag]]):
        self._email = value if value else ''

    @property
    def phone(self) -> Union[str, List[Tag]]:
        return self._phone

    @phone.setter
    def phone(self, value: Union[str, List[Tag]]):
        self._phone = value if value else ''

    @property
    def photo(self) -> Image:
        return self._photo

    @photo.setter
    def photo(self, value: Image):
        self._photo = value if value and isinstance(value,Image) else None

    @property
    def office(self) -> Union[str, List[Tag]]:
        return self._office

    @office.setter
    def office(self, value: Union[str, List[Tag]]):
        self._office = value if value else ''

    @property
    def website(self) -> Union[str, List[Tag]]:
        return self._website

    @website.setter
    def website(self, value: Union[str, List[Tag]]):
        self._website = value if value else ''


@dataclass
class StaffLookup:
    params: LookupParameters
    persons: Lookup
    details_url: Lookup

    @classmethod
    def from_dict(cls, d: Dict):
        fields = [f.name for f in dataclasses.fields(cls)]
        if not all([str(k).lower() in fields for k in d.keys()]):
            return None
        params = LookupParameters.from_dict(d['params'])
        persons = construct_lookup(d['persons'])
        details_url = construct_lookup(d['details_url'])
        return StaffLookup(params=params, persons=persons, details_url=details_url)

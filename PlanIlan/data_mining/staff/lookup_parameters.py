import dataclasses
import re
from dataclasses import dataclass, field
from enum import Enum, unique, auto
from typing import Union, List, Dict, ClassVar, Set

from bs4.element import Tag

from PlanIlan.utils.general import name_of

JOINT_SEPARATOR = '###'


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
    key: str = field(default=None)
    selector_method: SelectorMethod = field(default=SelectorMethod.FIND)
    _value: Union[str, int, List[str]] = field(init=False, default=None, compare=False)
    _regex: re.Pattern = field(init=False, compare=False, default=None)
    _tags: Set[str] = field(init=False, compare=False, default_factory=set)
    separators: ClassVar[List[str]] = [',', '|']
    css_selectors: ClassVar[List[str]] = ['>', '<', ' ']

    def __post_init__(self) -> None:
        if self.key is None:
            return
        if any(selector in self.key for selector in self.css_selectors):
            self.selector_method = SelectorMethod.SELECT
            return
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
                    self._tags.add(tag)
                else:
                    class_patterns.append(key)
            pattern = '|'.join(class_patterns)
        self._regex = re.compile(pattern)

    @property
    def is_valid(self) -> bool:
        return self.key is not None

    @property
    def has_value(self) -> bool:
        return self._value is not None

    @property
    def value(self) -> Union[str, int, List[str]]:
        ret = self._value
        if isinstance(self._value, List):
            ret = self._value.copy()
        return ret

    def __bool__(self):
        return self.is_valid

    def get_tags(self, web_element: Tag) -> List[Tag]:
        if self.selector_method == SelectorMethod.SELECT:
            tags = web_element.select(self.key)
        else:
            if self._regex is not None:
                tags = web_element.find_all(self._tags, class_=self._regex)
            else:
                tags = web_element.find_all(self._tags)
        return tags

    def get_single_tag(self, web_element: Tag) -> Tag:
        if self.selector_method == SelectorMethod.SELECT:
            tag = web_element.select_one(self.key)
        else:
            if self._regex is not None:
                tag = web_element.find(self._tags, class_=self._regex)
            else:
                tag = web_element.find(self._tags)
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
    office: Lookup = field(default_factory=Lookup)
    website: Lookup = field(default_factory=Lookup)

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

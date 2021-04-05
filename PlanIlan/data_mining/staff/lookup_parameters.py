import dataclasses
from dataclasses import dataclass, field
from enum import Enum, unique, auto
from typing import Union, List, Dict

from PlanIlan.utils.general import name_of


def construct_lookup(v: Union[Dict, str]):
    if not isinstance(v, (Dict, str)):
        raise ValueError(f'{name_of(v)} must be of type {(Dict, str)}')
    if isinstance(v, Dict):
        if 'key' not in v:
            raise ValueError('Lookup dict must contain "key" entry')
        key = v['key']
        selector = SelectorType.get_selector_type_by_name(v['selector']) if 'selector' in v else SelectorType.CLASS
    else:
        key = v
        selector = SelectorType.CLASS
    return Lookup(key=key, selector=selector)


@unique
class SelectorType(Enum):
    CLASS = auto()
    ID = auto()
    X_PATH = auto()

    @classmethod
    def get_selector_type_by_name(cls, name: str) -> 'SelectorType':
        return cls.__members__[name.upper()]


@dataclass
class Lookup:
    key: str = field(default=None)
    selector_type: SelectorType = field(default=SelectorType.CLASS)
    value: Union[str, int, List[str]] = field(default=None)

    @property
    def is_valid(self):
        return self.key is not None

    @property
    def has_value(self):
        return self.value is not None

    def __bool__(self):
        return self.is_valid


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
        photo = construct_lookup(d['photo'])
        office = construct_lookup(d['office']) if 'office' in d else Lookup()
        website = construct_lookup(d['website']) if 'website' in d else Lookup()
        return LookupParameters(name=name, title=title, email=email,
                                phone=phone, photo=photo, office=office, website=website)


@dataclass
class StaffLookup:
    params: LookupParameters
    persons: Lookup
    url: Lookup

import os
from collections import OrderedDict
from typing import List

from decouple import AutoConfig, RepositoryIni, DEFAULT_ENCODING


class SectionMissingInIniFile(Exception):
    pass


class KeyInMultipleSections(Exception):
    pass


class CostumeRepositoryIni(RepositoryIni):

    def __init__(self, source='', encoding=DEFAULT_ENCODING, sections: List[str] = None, ):
        super().__init__(source, encoding)
        self._source = source
        if sections is not None and any(not self.parser.has_section(section) for section in sections):
            raise SectionMissingInIniFile(f'all sections [{",".join(sections)}] must be in your file')
        self._sections = sections

    @property
    def sections(self):
        return self._sections

    @sections.setter
    def sections(self, sections: OrderedDict):
        self._sections = sections

    @property
    def source(self):
        return self._source

    def __contains__(self, key):
        return key in os.environ or self._get_value_from_key(key) is not None

    def _get_value_from_key(self, key: str, raise_error_if_multiple=True):
        value = None
        found_in_section = ''
        for section in self.sections:
            if not self.parser.has_option(section, key):
                continue
            elif value is not None:
                if raise_error_if_multiple:
                    raise KeyInMultipleSections(f'{key} appears in multiple sections ({found_in_section}, {section})')
                if isinstance(value, list):
                    value.append(self.parser.get(section, value))
                else:
                    value = [value, self.parser.get(section, value)]
            else:
                value = self.parser.get(section, key)
            found_in_section = section
        return value

    def __getitem__(self, key):
        return self._get_value_from_key(key)


class PlanIlanConfig(AutoConfig):

    def __init__(self, supported: OrderedDict, sections: OrderedDict, search_path=None):
        super().__init__(search_path)
        self.SUPPORTED = supported
        self.SECTIONS = sections

    def _load(self, path):
        super()._load(path)
        self.config.repository.sections = self.SECTIONS[os.path.basename(self.config.repository.source)]


SUPPORTED = OrderedDict([
    ('secrets.ini', CostumeRepositoryIni),
])
SECTIONS = OrderedDict([
    ('secrets.ini', ['general_settings', 'databases', 'email_backend'])
])
config = PlanIlanConfig(SUPPORTED, SECTIONS)

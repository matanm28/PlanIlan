from typing import List


class CommaSeparatedIntegerListConverter:
    regex = '(\d+)?(\^,(\d+))*'

    def to_python(self, value: str) -> List[int]:
        return map(int, value.split(','))

    def to_url(self, value: List[int]) -> str:
        return ','.join(map(str, value))

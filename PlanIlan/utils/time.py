import math
from datetime import time, timedelta
from dataclasses import dataclass, field
from typing import ClassVar, Union


@dataclass(order=True)
class TimeDelta:
    _total_seconds: int = field(default=0)

    def __init__(self, hours=0, minutes=0, seconds=0, **kwargs):
        if 'total_seconds' in kwargs:
            self._total_seconds = kwargs['total_seconds']
        else:
            self._total_seconds = (hours * 60 + minutes) * 60 + seconds

    @property
    def hours(self) -> int:
        return math.copysign(math.floor(abs(self._total_seconds) / (60 ** 2)), self._total_seconds)

    @property
    def minutes(self) -> int:
        return math.copysign(math.floor((abs(self._total_seconds) / 60) % 60), self._total_seconds)

    @property
    def seconds(self) -> int:
        return math.copysign(math.floor(abs(self._total_seconds) % 60), self._total_seconds)

    @property
    def total_seconds(self) -> int:
        return self._total_seconds

    @property
    def total_minutes(self) -> int:
        return self.hours * 60 + self.minutes

    def __add__(self, other: 'TimeDelta') -> 'TimeDelta':
        return TimeDelta(total_seconds=self._total_seconds + other._total_seconds)

    def __sub__(self, other: 'TimeDelta') -> 'TimeDelta':
        return TimeDelta(total_seconds=self._total_seconds - other._total_seconds)


@dataclass(frozen=True, order=True)
class Time:
    hour: int = field(default=0)
    minute: int = field(default=0)
    second: int = field(default=0)

    def __post_init__(self):
        validations_list = [0 <= self.hour < 24, 0 <= self.minute < 60, 0 <= self.second < 60]
        if not all(validations_list):
            raise ValueError

    @classmethod
    def min(cls):
        return Time()

    @classmethod
    def max(cls):
        return Time(23, 59, 59)

    def __add__(self, time_delta: TimeDelta) -> 'Time':
        second = self.second + time_delta.seconds
        minutes = self.minute + time_delta.minutes + math.floor(second / 60)
        hour = self.hour + time_delta.hours + math.floor(minutes / 60)
        return Time(math.floor(hour % 24), math.floor(minutes % 60), math.floor(second % 60))

    def __sub__(self, time_delta: TimeDelta) -> 'Time':
        loan = 0
        second = self.second - time_delta.seconds
        if second < 0:
            loan = abs(math.floor(second / 60))
            second %= 60
        minute = self.minute - time_delta.minutes + loan
        if minute < 0:
            loan = abs(math.floor(minute / 60))
            minute %= 60
        hour = (self.hour - time_delta.hours) % self.hour
        hour = (hour - loan) % hour
        return Time(hour % 24, minute % 60, second % 60)

    @classmethod
    def from_string(cls, time_str: str, delimiter=':'):
        time_list = []
        for t in time_str.split(delimiter):
            if t.isnumeric():
                time_list.append(int(t))
        for i in range(3-len(time_list)):
            time_list.append(0)
        return Time(*time_list[:3])

    def __str__(self) -> str:
        return f'{self.hour:02d}:{self.minute:02d}{f":{self.minute:02d}" if self.second>0 else ""}'





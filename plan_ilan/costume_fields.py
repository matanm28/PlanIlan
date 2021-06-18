from datetime import datetime, date, time, timedelta
from typing import Union

from django.db import models

# todo: delete
class ImprovedTimeField(models.TimeField):
    def __add__(self, other: timedelta) -> time:
        if isinstance(other, timedelta):
            return (datetime.combine(date.today(), self) - other).time()
        else:
            raise ValueError('other should be timedelta')

    def __sub__(self, other: Union[timedelta, time]) -> Union[time, float]:
        if isinstance(other, timedelta):
            return (datetime.combine(date.today(), self) - other).time()
        elif isinstance(other, time):
            today = date.today()
            return (datetime.combine(today, self) - datetime.combine(today, other)).total_seconds()
        else:
            raise ValueError('other should be Union[timedelta, time]')

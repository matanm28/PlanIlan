from datetime import datetime

from django.contrib.auth.forms import User as DjangoUser
from django.core.exceptions import MultipleObjectsReturned
from django.db import models

from . import Faculty, FacultyEnum, BaseModel

MIN_PASS_LENGTH = 8


def bytes_to_bits_string(bytes_str: str, strip_prefix=True):
    bits_str = bin(int.from_bytes(bytes_str, byteorder='big'))
    return bits_str.strip('0b') if strip_prefix else bits_str


def generate_account_id() -> int:
    return Account.objects.count() + 1


class Account(BaseModel):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, related_name='account')
    email = models.EmailField(verbose_name='email address', unique=True, max_length=100, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='accounts', default=FacultyEnum.UNKNOWN)

    class Meta:
        ordering = ['pk', 'faculty']
        db_table = 'accounts'

    def create(self, user_name: str, password: str, email: str, first_name: str, last_name: str, faculty: Faculty):
        pass

    def __str__(self):
        return self.username

    @classmethod
    def get_user_by_user_name(cls, name: str) -> 'Account':
        try:
            return Account.objects.get(user_name=name)
        except (models.Model.DoesNotExist, MultipleObjectsReturned) as err:
            # todo add logging - for entire project
            return None

    @property
    def username(self) -> str:
        return self.user.username

    @property
    def first_name(self) -> str:
        return self.user.first_name

    @property
    def last_name(self) -> str:
        return self.user.last_name

    @property
    def full_name(self) -> str:
        return self.user.get_full_name()

    @property
    def date_joined(self) -> datetime:
        return self.user.date_joined

    @property
    def last_login(self) -> datetime:
        return self.user.last_login

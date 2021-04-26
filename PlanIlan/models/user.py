from django.contrib.auth.forms import User as DjangoUser
from django.db import models
from django.db.models import Model

from PlanIlan.models import Faculty, FacultyEnum
from PlanIlan.models.base_model import BaseModel

MIN_PASS_LENGTH = 8


def bytes_to_bits_string(bytes_str: str, strip_prefix=True):
    bits_str = bin(int.from_bytes(bytes_str, byteorder='big'))
    return bits_str.strip('0b') if strip_prefix else bits_str


class User(BaseModel):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, related_name='app_user')
    user_name = models.CharField(primary_key=True, max_length=30, editable=False)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='users', default=FacultyEnum.UNKNOWN)
    email = models.EmailField(editable=False, unique=True)

    def __str__(self):
        return self.user_name

    @classmethod
    def get_user_by_user_name(cls, name: str) -> 'User':
        try:
            return User.objects.get(user_name=name)
        except (Model.DoesNotExist, Model.MultipleObjectsReturned) as err:
            # todo add logging - for entire project
            return None

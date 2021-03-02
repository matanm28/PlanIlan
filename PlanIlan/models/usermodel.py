import hashlib
import uuid
from django.db import models
from django.db.models import Model
from django.contrib.auth.forms import User

from PlanIlan.models.base_model import BaseModel

MIN_PASS_LENGTH = 8


def bytes_to_bits_string(bytes_str: str, strip_prefix=True):
    bits_str = bin(int.from_bytes(bytes_str, byteorder='big'))
    return bits_str.strip('0b') if strip_prefix else bits_str


class UserModel(BaseModel):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    user_name = models.CharField(primary_key=True, unique=True, max_length=30, editable=False)
    faculty = models.CharField(max_length=30, null=True)
    email = models.EmailField(editable=False, null=True)

    def __str__(self):
        return self.user_name

    @classmethod
    def get_user_by_user_name(cls, name: str) -> 'User':
        try:
            return UserModel.objects.get(user_name=name)
        except (Model.DoesNotExist, Model.MultipleObjectsReturned) as err:
            # todo add logging - for entire project
            return None

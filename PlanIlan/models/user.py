import hashlib
import uuid
from django.db import models
from django.db.models import Model

from PlanIlan.models.base_model import BaseModel

MIN_PASS_LENGTH = 8


def bytes_to_bits_string(bytes_str: str, strip_prefix=True):
    bits_str = bin(int.from_bytes(bytes_str, byteorder='big'))
    return bits_str.strip('0b') if strip_prefix else bits_str


class User(BaseModel):
    user_name = models.CharField(primary_key=True, unique=True, max_length=30, editable=False)
    email = models.EmailField(editable=False)
    salt = models.UUIDField(editable=False)
    password_hash = models.BinaryField(max_length=1024, editable=False)

    def __str__(self):
        return self.user_name

    @classmethod
    def create(cls, user_name: str, email: str, password: str) -> 'User':
        salt = uuid.uuid4()
        hashed_pass = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt.hex.encode('utf-8'), 100000, dklen=128)
        user, created = User.objects.get_or_create(user_name=user_name,
                                                   defaults={'email': email, 'salt': salt,
                                                             'password_hash': hashed_pass})
        cls.log_created(cls.__name__, user_name, created)
        return user

    @classmethod
    def get_user_by_user_name(cls, name: str) -> 'User':
        try:
            return User.objects.get(user_name=name)
        except (Model.DoesNotExist, Model.MultipleObjectsReturned) as err:
            # todo add logging - for entire project
            return None

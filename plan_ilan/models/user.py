import hashlib
import uuid

from django.db import models

MIN_PASS_LENGTH = 8


def bytes_to_bits_string(bytes_str: str, strip_prefix=True):
    bits_str = bin(int.from_bytes(bytes_str, byteorder='big'))
    return bits_str.strip('0b') if strip_prefix else bits_str


class User(models.Model):
    user_name = models.CharField(primary_key=True, unique=True, max_length=30, editable=False)
    email = models.EmailField(editable=False)
    salt = models.UUIDField(editable=False)
    password_hash = models.BinaryField(max_length=1024, editable=False)

    @classmethod
    def create(cls, user_name: str, email: str, password: str):
        salt = uuid.uuid4()
        hashed_pass = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt.hex,
            100000,
            dklen=128
        )
        user = User(user_name=user_name, email=email, salt=salt, password_hash=hashed_pass)
        user.save()

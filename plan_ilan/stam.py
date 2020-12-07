import hashlib
import uuid

from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

MIN_RATING, MAX_RATING = 0, 5
VALIDATORS = [MinValueValidator(MIN_RATING, f'Value should not fall short of {MIN_RATING}'),
              MaxValueValidator(MAX_RATING, f'Value should not exceed {MAX_RATING}')]

MIN_PASS_LENGTH = 8


def bytes_to_bits_string(bytes_str: str, strip_prefix=True):
    bits_str = bin(int.from_bytes(bytes_str, byteorder='big'))
    return bits_str.strip('0b') if strip_prefix else bits_str


class Day(models.IntegerChoices):
    SUNDAY = 1, _('ראשון')
    MONDAY = 2, _('שני')
    TUESDAY = 3, _('שלישי')
    WEDNESDAY = 4, _('רביעי')
    THURSDAY = 5, _('חמישי')
    FRIDAY = 6, _('שישי')


class Faculty(models.IntegerChoices):
    CS = 89, _('מדעי המחשב')

    @classmethod
    def get_faculty_by_number(cls, num: int):
        for faculty in cls.choices:
            if faculty == num:
                return faculty
        return cls.CS


class Semester(models.IntegerChoices):
    FIRST = 1, _("סמסטר א'")
    SECOND = 2, _("סמסטר ב'")


class SessionType(models.IntegerChoices):
    LECTURE = 0, _('הרצאה')
    RECITATION = 1, _('תרגול')
    REINFORCING = 2, _('תגבור')


class TeacherTitle(models.IntegerChoices):
    DOC = 0, _('ד"ר')
    PROF = 1, _("פרופ'")
    MR = 2, _('מר')
    MRS = 3, _('גברת')


class LessonTime(models.Model):
    day = models.IntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @property
    def duration(self):
        return datetime(self.end_time) - datetime(self.start_time)


class Location(models.Model):
    building_name = models.CharField(max_length=80)
    building_number = models.IntegerField(null=True)
    class_number = models.IntegerField(null=True)
    online = models.BooleanField(default=False)


class Post(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)
    amount_of_likes = models.IntegerField(default=0)
    headline = models.CharField(max_length=256)
    text = models.TextField()

    class Meta:
        abstract = True


class TeacherPost(Post):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)


class CoursePost(Post):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)


class Rating(models.Model):
    average = models.IntegerField(validators=VALIDATORS)
    amount_of_raters = models.IntegerField(default=0,
                                           validators=[MinValueValidator(0, 'Value has to be a natural number')])

    class Meta:
        abstract = True


class TeacherRating(Rating):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)


class CourseRating(Rating):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)


class Teacher(models.Model):
    name = models.CharField(primary_key=True, max_length=80)
    title = models.IntegerField(choices=TeacherTitle.choices)


class Course(models.Model):
    course_id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=80)
    teacher_name = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    lesson_times = models.ManyToManyField('LessonTime')
    locations = models.ManyToManyField('Location')
    faculty = models.IntegerField(choices=Faculty.choices)
    semester = models.IntegerField(choices=Semester.choices)
    details_link = models.URLField(null=True)

    @property
    def group_code(self):
        return self.course_id[-2:]

    @property
    def code(self):
        return self.course_id[:-2]

    @property
    def faculty_code(self):
        return self.course_id[:2]


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

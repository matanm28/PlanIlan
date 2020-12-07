from django.db import models
from django.utils.translation import gettext_lazy as _


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
    def get_faculty_by_number(cls, num:int):
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

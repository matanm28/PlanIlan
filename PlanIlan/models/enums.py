from typing import Tuple

from django.db import models
from django.utils.translation import gettext_lazy as _

from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError


class LabeledIntegerEnum(models.IntegerChoices):
    @classmethod
    def from_string(cls, search_value: str) -> 'LabeledIntegerEnum':
        for enum in cls:
            if search_value in enum.label:
                return enum
        raise EnumNotExistError(cls.__name__, search_value)

    @classmethod
    def from_int(cls, search_value: int) -> 'LabeledIntegerEnum':
        for enum in cls:
            if enum.value == search_value:
                return enum
        raise EnumNotExistError(cls.__name__, search_value)

    @classmethod
    def from_name(cls, search_value: str) -> 'LabeledIntegerEnum':
        for enum in cls:
            if search_value in enum.name:
                return enum
        raise EnumNotExistError(cls.__name__, search_value)


class Day(LabeledIntegerEnum):
    SUNDAY = 1, _('א')
    MONDAY = 2, _('ב')
    TUESDAY = 3, _('ג')
    WEDNESDAY = 4, _('ד')
    THURSDAY = 5, _('ה')
    FRIDAY = 6, _('ו')

    @classmethod
    def full_strings_labels(cls) -> Tuple[str]:
        return 'ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי'

    @property
    def full_label(self) -> str:
        return Day.full_strings_labels()[Day.labels.indexof(self.label)]


class Faculty(LabeledIntegerEnum):
    NULL_FACULTY = -1, _('לא קיים')
    YESSOD_BIBLE = 1, _('לימודי יסוד - תנ"ך')
    YESSOD_TALMUD = 2, _('לימודי יסוד - תלמוד')
    JUD_PHIL = 3, _('פילוסופיה יהודית')
    YESSOD_ISR = 4, _('לימודי יסוד - תולדות ישראל')
    WOMEN_MIDRASHA = 5, _('המדרשה לנשים')
    EXP = 6, _('הבעה אקדמית ואולפן')
    BIBLE = 8, _('תנ"ך')
    TALMUD_TOSHBA = 9, _('תלמוד ותושב"ע')
    TOSHBA = 10, _('תושב"ע')
    JEW_HIST = 11, _('תולדות ישראל ויהדות זמננו')
    SPEECH = 12, _('המחלקה ללשון עברית וללשונות שמיות')
    LIT_ISR = 13, _('ספרות עם ישראל')
    ISR = 16, _('לימודי ארץ ישראל וארכיאולוגיה')
    JUD = 17, _('מדעי היהדות')
    HIST = 18, _('הסטוריה כללית')
    M_EAST = 19, _('מזרח התיכון')
    ART = 21, _('אמנות יהודית')
    EDIT = 22, _('לימודי תעודה בעריכה')
    BROK = 25, _('תכנית ברוקדייל')
    INTER = 27, _('לימודי פרשנות ותרבות')
    JUD_CALC = 30, _('מחשבת ישראל')
    PHIL = 31, _('פילוסופיה')
    LIT = 33, _('ספרות')
    INFO = 35, _('מדעי המידע')
    ARABIC = 36, _('המחלקה לערבית')
    LING = 37, _('בלשנות וספרות אנגלית')
    ENG = 41, _('אנגלית כשפה זרה')
    FR = 43, _('המחלקה לתרבות צרפת')
    CLASSIC = 46, _('לימודים קלאסיים')
    MUSIC = 47, _('מוסיקה')
    TRANS = 50, _('תרגום וחקר התרגום')
    HUM = 54, _('מדעי הרוח')
    MANAGEMENT = 55, _('המחלקה לניהול')
    PSY = 60, _('פסיכולוגיה')
    COMM = 63, _('ביה"ס לתקשורת')
    SOCIOLOGY = 64, _('סוציולוגיה ואנתרופולוגיה')
    ECO = 66, _('כלכלה')
    BUSINESS = 70, _('מינהל עסקים')
    COUNT = 71, _('מדעי המדינה')
    GOVERNMENT = 72, _('המכון לשלטון מקומי')
    CRIME = 73, _('קרימינולוגיה')
    SOCIAL = 74, _('מדעי החברה')
    GEO = 75, _('גיאוגרפיה')
    SOC = 76, _('עבודה סוציאלית')
    EDU = 77, _('חינוך')
    INSTRUCT = 79, _('הוראה')
    LIFE = 80, _('מדעי החיים')
    MD = 81, _('הפקולטה לרפואה')
    OPTIMETRICS = 82, _('אופטימטריה')
    ENGINEERING = 83, _('הנדסה')
    CHEM = 84, _('כימיה')
    PHY = 86, _('פיסיקה')
    MATH = 88, _('מתמטיקה')
    CS = 89, _('למדעי המחשב')
    MULTI = 93, _('רב תחומי')
    DIPLOMA = 94, _('דיפלומה')
    LAW = 99, _('הפקולטה למשפטים')
    NEUROSCIENCE = 272, _('מדעי המוח')
    GENDER = 273, _('לימודי מגדר')
    NEUROSCIENCE_ADVANCED = 275, _('מדעי המוח לתארים מתקדמים')


class Semester(LabeledIntegerEnum):
    FIRST = 1, _("סמסטר א'")
    SECOND = 2, _("סמסטר ב'")
    SUMMER = 3, _("סמסטר קיץ")
    YEARLY = 4, _('שנתי')


class SessionType(LabeledIntegerEnum):
    LECTURE = 0, _('הרצאה')
    RECITATION = 1, _('תרגול')
    REINFORCING = 2, _('תגבור')
    SEMINAR = 3, _('סמינריון')


class TeacherTitle(LabeledIntegerEnum):
    DOC = 0, _('ד"ר')
    PROF = 1, _("פרופ'")
    MR = 2, _('מר')
    MRS = 3, _('גברת')


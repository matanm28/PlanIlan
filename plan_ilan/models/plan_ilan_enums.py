from django.db import models
from django.utils.translation import gettext_lazy as _


class Day(models.IntegerChoices):
    SUNDAY = 1, _('ראשון')
    MONDAY = 2, _('שני')
    TUESDAY = 3, _('שלישי')
    WEDNESDAY = 4, _('רביעי')
    THURSDAY = 5, _('חמישי')
    FRIDAY = 6, _('שישי')

    @classmethod
    def get_enum(cls, day: str):
        day = day.rstrip()
        if 'א' in day:
            return cls.SUNDAY
        elif 'ב' in day:
            return cls.MONDAY
        elif 'ג' in day:
            return cls.TUESDAY
        elif 'ד' in day:
            return cls.WEDNESDAY
        elif 'ה' in day:
            return cls.THURSDAY
        elif 'ו' in day:
            return cls.FRIDAY


class Faculty(models.IntegerChoices):
    CS = 89, _('למדעי המחשב')
    NEUROSCIENCE = 27, _('מדעי המוח')
    ARABIC = 36, _('המחלקה לערבית')
    OPT = 82, _('אופטימטריה')
    MANAGEMENT = 55, _('המחלקה לניהול')
    BUSINESS = 70, _('מינהל עסקים')
    COMM = 63, _('ביה"ס לתקשורת')
    EDU = 77, _('חינוך')
    DIPLOMA = 94, _('דיפלומה')
    MIDRASHA = 5, _('המדרשה לנשים')
    ECO = 66, _('כלכלה')
    TUSHBA = 10, _('תושב"ע')
    SOCIAL = 74, _('מדעי החברה')
    CHEM = 84, _('כימיה')
    GEO = 75, _('גיאוגרפיה')
    INSTRUCT = 79, _('הוראה')
    BROK = 25, _('תכנית ברוקדייל')
    GENDER = 27, _('לימודי מגדר')
    FR = 43, _('המחלקה לתרבות צרפת')
    MD = 81, _('הפקולטה לרפואה')
    LAW = 99, _('הפקולטה למשפטים')
    GOVER = 72, _('המכון לשלטון מקומי')
    HUM = 54, _('מדעי הרוח')
    MULTI = 93, _('רב תחומי')
    SOC = 76, _('עבודה סוציאלית')
    JUD = 17, _('מדעי היהדות')
    ENG = 41, _('אנגלית כשפה זרה')
    EXP = 6, _('הבעה אקדמית ואולפן')
    ART = 21, _('אמנות יהודית')
    LING = 37, _('בלשנות וספרות אנגלית')
    HIST = 18, _('הסטוריה כללית')
    ISR = 16, _('לימודי ארץ ישראל וארכיאולוגיה')
    M_EAST = 19, _('מזרח התיכון')
    CLASSIC = 46, _('לימודים קלאסיים')
    SPEECH = 12, _('המחלקה ללשון עברית וללשונות שמיות')
    COUNT = 71, _('מדעי המדינה')
    INFO = 35, _('מדעי המידע')
    MUSIC = 47, _('מוסיקה')
    JUD_CALC = 30, _('מחשבת ישראל')
    MATH = 88, _('מתמטיקה')
    SOCIO = 64, _('סוציולוגיה ואנתרופולוגיה')
    LIT = 33, _('ספרות')
    LIT_ISR = 13, _('ספרות עם ישראל')
    PHIL = 31, _('פילוסופיה')
    PHY = 86, _('פיסיקה')
    PSY = 60, _('פסיכולוגיה')
    CRIME = 73, _('קרימינולוגיה')
    JEW_HIST = 11, _('תולדות ישראל ויהדות זמננו')
    TALMUD_TUSHBA = 9, _('תלמוד ותושב"ע')
    BIBLE = 8, _('תנ"ך')
    TRNS = 50, _('תרגום וחקר התרגום')
    ENGINEER = 83, _('הנדסה')
    LIFE = 80, _('מדעי החיים')
    JUD_PHIL = 3, _('פילוסופיה יהודית')
    BASE_ISR = 4, _('לימודי יסוד - תולדות ישראל')
    BASE_TALMUD = 2, _('לימודי יסוד - תלמוד')
    BASE_BIBLE = 1, _('לימודי יסוד - תנ"ך')
    INTER = 27, _('פרשנות')
    EDIT = 22, _('לימודי תעודה בעריכה')
    ISR = 16, _('לימודי ארץ ישראל וארכיאולוגיה')


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

    @classmethod
    def get_enum(cls, title_str: str):
        title_str = title_str.rstrip()
        if title_str[0] in cls.DOC:
            return cls.DOC
        elif title_str[0] in cls.PROF:
            return cls.PROF
        elif title_str[0] in cls.MR:
            return cls.MR
        elif title_str[0] in cls.MRS:
            return cls.MRS

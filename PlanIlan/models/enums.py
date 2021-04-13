from typing import Tuple

from django.db import models
from django.utils.translation import gettext_lazy as _

from PlanIlan.exceptaions.enum_not_exist_error import EnumNotExistError


class LabeledTextEnum(models.TextChoices):
    @classmethod
    def from_string(cls, search_value: str) -> 'LabeledTextEnum':
        for enum in cls:
            if search_value in enum.label:
                return enum
        raise EnumNotExistError(cls.__name__, search_value)

    @classmethod
    def from_number(cls, search_value: str) -> 'LabeledTextEnum':
        for enum in cls:
            if enum.value == search_value:
                return enum
        raise EnumNotExistError(cls.__name__, search_value)

    @classmethod
    def from_name(cls, search_value: str) -> 'LabeledTextEnum':
        for enum in cls:
            if search_value in enum.name:
                return enum
        raise EnumNotExistError(cls.__name__, search_value)


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


class DayEnum(LabeledIntegerEnum):
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
        return DayEnum.full_strings_labels()[DayEnum.labels.indexof(self.label)]


class DepartmentEnum(LabeledIntegerEnum):
    NULL_DEPARTMENT = -1, _('לא קיים')
    HUMAN_STUDIES = 0, _('ב.א. רב תחומי במדעי הרוח')
    MULTI_DISCIPLINARY = 1, _('ב.א. רב-תחומי')
    OPTOMETRY = 2, _('ביה"ס לאופטומטריה ומדעי הראייה')
    LAW_SCHOOL = 3, _('ביה"ס ללימודי משפט')
    BUSINESS = 4, _('ביה"ס למינהל עסקים')
    PRESS = 5, _('ביה"ס לתקשורת')
    EDUCATION_PINHAS_HORGIN = 6, _('בית הספר לחינוך ע"ש פנחס חורגין')
    SOCIAL_WORK = 7, _('בית הספר לעבודה סוציאלית ע"ש לואיס וגבי וייספלד')
    DIPLOMA = 8, _('דיפלומה')
    JOINT_SOCIAL_STUDIES = 9, _('החוג המשולב במדעי החברה')
    JUDAISM = 10, _('החוג הרב-תחומי במדעי היהדות')
    ENGLISH = 11, _('היחידה לאנגלית כשפה זרה')
    ULPAN = 12, _('היחידה להבעה אקדמית ואולפן')
    PRESS_STUDIES_UNIT = 13, _('היחידה ללימודי תקשורת ועיתונאות')
    LANGUAGES = 14, _('היחידה לשפות')
    TOSHBA = 15, _('המגמה לתושב"ע')
    WOMEN_MIDRASHA = 16, _('המדרשה לנשים')
    JEW_ART = 17, _('המחלקה לאמנות יהודית')
    LITERATURE = 18, _('המחלקה לבלשנות וספרות אנגלית')
    GEOGRAPHY = 19, _('המחלקה לגיאוגרפיה וסביבה')
    GENERAL_HISTORY = 20, _('המחלקה להסטוריה כללית')
    CHEMISTRY = 21, _('המחלקה לכימיה')
    ECONOMICS = 22, _('המחלקה לכלכלה')
    ARCHAEOLOGY = 23, _('המחלקה ללימודי ארץ ישראל וארכיאולוגיה')
    MIDDLE_EAST_STUDIES = 24, _('המחלקה ללימודי המזרח התיכון')
    CLASSIC = 25, _('המחלקה ללימודים קלאסיים')
    LASHON_IVRIT = 26, _('המחלקה ללשון העברית וללשונות שמיות')
    POLITICAL_SCIENCE = 27, _('המחלקה למדעי המדינה')
    COMPUTER_SCIENCE = 28, _('המחלקה למדעי המחשב')
    INFORMATION_SCIENCE = 29, _('המחלקה למדעי המידע')
    MUSIC = 30, _('המחלקה למוזיקה')
    MACHSHEVET_ISRAEL = 31, _('המחלקה למחשבת ישראל')
    MATHEMATICS = 32, _('המחלקה למתמטיקה')
    MANAGEMENT = 33, _('המחלקה לניהול')
    SOCIOLOGY = 34, _('המחלקה לסוציולוגיה ואנתרופולוגיה')
    SAFRUT_MASHVA = 35, _('המחלקה לספרות משווה')
    SAFRUT_OF_ISRAEL = 36, _('המחלקה לספרות עם ישראל ע"ש יוסף ונחום ברמן')
    ARABIC = 37, _('המחלקה לערבית')
    PHILOSOPHY = 38, _('המחלקה לפילוסופיה')
    PHYSICS = 39, _('המחלקה לפיזיקה')
    PSYCHOLOGY = 40, _('המחלקה לפסיכולוגיה')
    CRIMINOLOGY = 41, _('המחלקה לקרימינולוגיה')
    JEWISH_HISTORY = 42, _('המחלקה לתולדות ישראל ויהדות זמננו')
    TALMUD_AND_TOSHBA = 43, _('המחלקה לתלמוד ותושב"ע ע"ש נפתלי יפה')
    BIBLE_ZALMAN_SHAMIR = 44, _('המחלקה לתנ"ך על שם זלמן שמיר')
    FRANCE = 45, _('המחלקה לתרבות צרפת')
    TRANSLATIONS_STUDIES = 46, _('המחלקה לתרגום וחקר התרגום')
    SHILTON_MEKOMI = 47, _('המכון לשלטון מקומי')
    ENGINEERING = 48, _('הפקולטה להנדסה ע"ש אלכסנדר קופקין')
    LIFE_SCIENCE = 49, _('הפקולטה למדעי החיים ע"ש מינה ואבררד גודמן')
    LAW = 50, _('הפקולטה למשפטים')
    MED_SCHOOL = 51, _('הפקולטה לרפואה')
    YAHADUT_ZMANENU = 52, _('יהדות זמננו')
    YESSOD_JEWISH_PHILOSOPHY = 53, _('לימודי יסוד - פילוסופיה יהודית')
    YESSOD_ISRAEL = 54, _('לימודי יסוד - תולדות ישראל')
    YESSOD_TALMUD = 55, _('לימודי יסוד - תלמוד')
    YESSOD_BIBLE = 56, _('לימודי יסוד - תנ"ך')
    GENDER = 57, _('לימודי מגדר')
    PARSHANUT_AND_TARBUT = 58, _('לימודי פרשנות ותרבות')
    EDIT = 59, _('לימודי תעודה בעריכה')
    MULTI_DISCIPLINARY_STUDIES = 60, _('לימודים בין-תחומיים')
    SCIENCE_TECH_SOCIETY = 61, _('מדע, טכנולוגיה וחברה')
    NEUROSCIENCE = 62, _('מדעי המוח')
    NEUROSCIENCE_ADVANCED = 63, _('מדעי המוח לתארים מתקדמים')
    CONFLICT_RESOLUTION = 64, _('ניהול ויישוב סכסוכים')
    FOREIGN_STUDIES = 65, _('ע"ס-לימודי חוץ')
    ART_HISTORY = 66, _('תולדות אמנות')
    BROKDAIL_PROGRAM = 67, _('תכנית ברוקדייל')
    TEODAT_HORAA = 68, _('תעודת הוראה')


class FacultyEnum(LabeledIntegerEnum):
    GENERAL = 0, _("כללי")
    LIFE_SCIENCES = 1, _("מדעי החיים ")
    JUDAISM_SCIENCES = 2, _("מדעי היהדות")
    LAW = 3, _("משפטים")
    MED = 4, _("רפואה")
    SOCIAL_SCIENCES = 5, _("מדעי החברה")
    ENGINEERING = 6, _("הנדסה ")
    EXACT_SCIENCES = 7, _("מדעים מדויקים")
    MULTI_DISCIPLINARY_UNIT = 8, _("יחידה ללימודים בין תחומיים")
    ARTS = 9, _("מדעי הרוח")
    UNKNOWN = 10, _("לא ידוע")

    @classmethod
    def from_string(cls, search_value: str) -> 'LabeledIntegerEnum':
        try:
            return super().from_string(search_value)
        except EnumNotExistError:
            return cls.UNKNOWN


class SemesterEnum(LabeledIntegerEnum):
    FIRST = 1, _("סמסטר א'")
    SECOND = 2, _("סמסטר ב'")
    SUMMER = 3, _("סמסטר ק'")
    YEARLY = 4, _('שנתי')


class ExamPeriodEnum(LabeledIntegerEnum):
    FIRST = 1, _("מועד א'")
    SECOND = 2, _("מועד ב'")
    THIRD = 3, _("מועד ג'")
    SPECIAL = 4, _("מועד מיוחד")

    @classmethod
    def from_string(cls, search_value: str) -> 'LabeledIntegerEnum':
        try:
            return super().from_string(search_value)
        except EnumNotExistError:
            return cls.SPECIAL


class SessionTypeEnum(LabeledIntegerEnum):
    LECTURE = 0, _('הרצאה')
    TIRGUL = 1, _('תרגול')
    REINFORCING = 2, _('תגבור')
    SEMINAR = 3, _('סמינריון')
    HEVROOTA = 4, _('חברותא')
    SADNA = 5, _('סדנה')


class TeacherTitleEnum(LabeledIntegerEnum):
    BLANK = -1, _('')
    DOC = 0, _('ד"ר')
    PROF = 1, _("פרופ'")
    MR = 2, _('מר')
    MRS = 3, _('גברת')
    RABBI = 4, _('הרב')
    LAWYER = 5, _('עו"ד')
    JUDGE = 6, _('השופט')

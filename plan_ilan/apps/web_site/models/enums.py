from typing import Tuple, Type

from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import gettext_lazy as _

from plan_ilan.apps.web_site.decorators import receiver_subclasses
from plan_ilan.exceptaions.enum_not_exist_error import EnumNotExistError
from . import BaseModel


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


# todo: change error to __empty__ or default enum
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


class EnumModel(BaseModel):
    number = models.SmallIntegerField(primary_key=True, editable=False)
    label = models.CharField(max_length=60, editable=False)

    @classmethod
    def get_enum_class(cls) -> Type[LabeledIntegerEnum]:
        pass

    @classmethod
    def create(cls, number: int) -> 'EnumModel':
        pass

    @classmethod
    def _get_enum_from_int(cls, num: int) -> LabeledIntegerEnum:
        return cls.get_enum_class().from_int(num)

    @classmethod
    def get_from_enum(cls, enum: LabeledIntegerEnum):
        return cls.objects.filter(pk=enum).first()

    @property
    def enum(self) -> LabeledIntegerEnum:
        return self.get_enum_class().from_int(self.number)

    def __repr__(self):
        return f'number:{self.number}, label:{self.label}'

    def __str__(self):
        return self.label

    class Meta:
        abstract = True
        unique_together = ['number', 'label']
        ordering = ['number']


class DAYS(LabeledIntegerEnum):
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
        return DAYS.full_strings_labels()[self.value - 1]

    def __str__(self):
        return self.full_label


class Day(EnumModel):
    FULL_STRINGS = ('ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי')

    class Meta(EnumModel.Meta):
        db_table = 'days'

    @classmethod
    def get_enum_class(cls) -> Type[LabeledIntegerEnum]:
        return DAYS

    @classmethod
    def create(cls, number: int) -> 'Day':
        enum = cls._get_enum_from_int(number)
        instance, created = Day.objects.get_or_create(number=enum.value, label=enum.label)
        cls.log_created(instance, created)
        return instance

    @property
    def full_label(self):
        return self.FULL_STRINGS[self.number - 1]

    def __repr__(self):
        return f'{super().__repr__()},full_label:{self.full_label}'

    def __str__(self):
        return self.full_label


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

    @classmethod
    def from_string(cls, search_value: str) -> 'LabeledIntegerEnum':
        try:
            return super().from_string(search_value)
        except EnumNotExistError:
            return cls.NULL_DEPARTMENT


class Department(EnumModel):
    class Meta(EnumModel.Meta):
        db_table = 'departments'

    @classmethod
    def get_enum_class(cls) -> Type[LabeledIntegerEnum]:
        return DepartmentEnum

    @classmethod
    def create(cls, number: int) -> 'Department':
        enum = cls._get_enum_from_int(number)
        instance, created = Department.objects.get_or_create(number=enum.value, label=enum.label)
        cls.log_created(instance, created)
        return instance


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


class Faculty(EnumModel):
    class Meta(EnumModel.Meta):
        db_table = 'faculties'

    @classmethod
    def get_enum_class(cls) -> Type[LabeledIntegerEnum]:
        return FacultyEnum

    @classmethod
    def create(cls, number: int) -> 'Faculty':
        enum = cls._get_enum_from_int(number)
        instance, created = Faculty.objects.get_or_create(number=enum.value, label=enum.label)
        cls.log_created(instance, created)
        return instance

    @classmethod
    def forms_queryset(cls):
        return Faculty.objects.exclude(pk=FacultyEnum.UNKNOWN)


class SemesterEnum(LabeledIntegerEnum):
    FIRST = 1, _("סמסטר א")
    SECOND = 2, _("סמסטר ב")
    SUMMER = 3, _("סמסטר ק")
    YEARLY = 4, _('שנתי')

    @classmethod
    def from_string(cls, search_value: str) -> 'LabeledIntegerEnum':
        return super().from_string(search_value.strip("'"))


class Semester(EnumModel):
    class Meta(EnumModel.Meta):
        db_table = 'semesters'

    @classmethod
    def get_enum_class(cls) -> Type[LabeledIntegerEnum]:
        return SemesterEnum

    @classmethod
    def create(cls, number: int) -> 'Semester':
        enum = cls._get_enum_from_int(number)
        instance, created = Semester.objects.get_or_create(number=enum.value, label=enum.label)
        cls.log_created(instance, created)
        return instance


class ExamPeriodEnum(LabeledIntegerEnum):
    FIRST = 1, _("מועד א")
    SECOND = 2, _("מועד ב")
    THIRD = 3, _("מועד ג")
    SPECIAL = 4, _("מועד מיוחד")

    @classmethod
    def from_string(cls, search_value: str) -> 'LabeledIntegerEnum':
        try:
            return super().from_string(search_value.strip("'"))
        except EnumNotExistError:
            return cls.SPECIAL


class ExamPeriod(EnumModel):
    class Meta(EnumModel.Meta):
        db_table = 'exam_periods'

    @classmethod
    def get_enum_class(cls) -> Type[LabeledIntegerEnum]:
        return ExamPeriodEnum

    @classmethod
    def create(cls, number: int) -> 'ExamPeriod':
        enum = cls._get_enum_from_int(number)
        instance, created = ExamPeriod.objects.get_or_create(number=enum.value, label=enum.label)
        cls.log_created(instance, created)
        return instance


class LessonTypeEnum(LabeledIntegerEnum):
    LECTURE = 0, _('הרצאה')
    TIRGUL = 1, _('תרגול')
    REINFORCING = 2, _('תגבור')
    SEMINAR = 3, _('סמינריון')
    HEVROOTA = 4, _('חברותא')
    SADNA = 5, _('סדנה')
    HAAZNA = 6, _('האזנה')
    SVEVKLINI = 7, _('סבב קליני')
    THEZA = 8, _('תיזה')
    GRADE = 9, _('ציון')
    QUALQIUM_MANDATORY = 10, _('קולוקויום חובה')
    MIUN = 11, _('מיון')
    STAZ = 12, _("סטאז'")
    HADRACHA = 13, _('הדרכה')
    BEHINA = 14, _('בחינה')
    MIRPAA = 15, _('מרפאה')
    AVODA = 16, _('עבודה')
    RISHUM = 17, _('רישום')
    MAABADA = 18, _('מעבדה')
    HACHSHARA = 19, _('הכשרה מעשית')
    DISATERAZIA = 20, _('דיסרטציה')
    PARKTIKUM = 21, _('פרקטיקום')
    TRAINING = 22, _('אימון')
    SIYUR = 23, _('סיור')
    QUALQIUM_ELECTIVE = 24, _('קולוקויום רשות')
    HAFIROT = 25, _('חפירות')
    PRO_SEMINAR = 26, _('פרו-סמינריון')
    PROJECT = 27, _('פרויקט')
    MACHLAKA_TIME = 28, _('ש.מחלקה')
    PTOR = 29, _('פטור')


class LessonType(EnumModel):
    class Meta(EnumModel.Meta):
        db_table = 'lesson_types'

    @classmethod
    def get_enum_class(cls) -> Type[LabeledIntegerEnum]:
        return LessonTypeEnum

    @classmethod
    def create(cls, number: int) -> 'LessonType':
        enum = cls._get_enum_from_int(number)
        instance, created = LessonType.objects.get_or_create(number=enum.value, label=enum.label)
        cls.log_created(instance, created)
        return instance


class TitleEnum(LabeledIntegerEnum):
    BLANK = 0, _('')
    DOC = 1, _('ד"ר')
    PROF = 2, _("פרופ'")
    MR = 3, _('מר')
    MRS = 4, _('גברת')
    RABBI = 5, _('הרב')
    LAWYER = 6, _('עו"ד')
    JUDGE = 7, _('השופט')


class Title(EnumModel):
    class Meta(EnumModel.Meta):
        db_table = 'titles'

    @classmethod
    def get_enum_class(cls) -> Type[LabeledIntegerEnum]:
        return TitleEnum

    @classmethod
    def create(cls, number: int) -> 'Title':
        enum = cls._get_enum_from_int(number)
        instance, created = Title.objects.get_or_create(number=enum.value, label=enum.label)
        cls.log_created(instance, created)
        return instance


@receiver_subclasses(pre_save, EnumModel, 'prevent_save_if_enum_not_valid', weak=False)
def pre_save_handler(sender, instance, *args, **kwargs):
    try:
        sender.get_enum_class().from_int(instance.number)
    except EnumNotExistError:
        raise Exception('enum is not defined')

from .course_serializers import CourseBasicSerializer, CourseExtendedSerializer, CourseFullDetailsSerializer, \
    CourseExtraDetailsSerializer, LessonBasicSerializer, LessonExtendedSerializer, LessonFullDetailsSerializer
from .general_serializers import EnumSerializer, LessonTimeSerializer, LocationSerializer, ExamSerializer
from .teacher_serializers import TeacherBasicSerializer, TeacherExtendedSerializer, TeacherFullDetailsSerializer
from .timetable_serializers import IntervalSerializer, TimeIntervalSerializer, BlockedTimePeriodSerializer, \
    RankedLessonSerializer, TimetableCommonInfoSerializer, TimetableSerializer

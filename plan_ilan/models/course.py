from django.db import models

from .plan_ilan_enums import Faculty, Semester


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

from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserModel)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(CoursePost)
admin.site.register(TeacherPost)
admin.site.register(Location)
admin.site.register(SessionTime)
admin.site.register(Rating)
admin.site.register(Day)

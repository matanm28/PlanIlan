from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserModel)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(CoursePost)
admin.site.register(TeacherPost)
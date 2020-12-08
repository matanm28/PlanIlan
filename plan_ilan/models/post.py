from datetime import datetime

from django.db import models


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

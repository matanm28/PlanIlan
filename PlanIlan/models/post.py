from datetime import datetime

from django.db import models

from PlanIlan.models import User, Teacher, Course, BaseModel


class Post(BaseModel):
    class Meta:
        abstract = True

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)
    amount_of_likes = models.IntegerField(default=0)
    headline = models.CharField(max_length=256)
    text = models.TextField()


class TeacherPost(Post):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='posts')

    @classmethod
    def create(cls, author_name: str, headline: str, text: str, teacher: Teacher) -> 'TeacherPost':
        user = User.get_user_by_user_name(author_name)
        if not user:
            return None
        post, created = TeacherPost.objects.get_or_create(author=user, headline=headline, text=text, Teacher=teacher)
        cls.log_created(cls.__name__, post.id, created)
        return post


class CoursePost(Post):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='posts')

    @classmethod
    def create(cls, author_name: str, headline: str, text: str, course: Course) -> 'CoursePost':
        user = User.get_user_by_user_name(author_name)
        if not user:
            return None
        post, created = CoursePost.objects.get_or_create(author=user, headline=headline, text=text, course=course)
        cls.log_created(cls.__name__, post.id, created)
        return post

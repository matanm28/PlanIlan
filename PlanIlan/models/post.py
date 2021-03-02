from datetime import datetime

from django.db import models

from PlanIlan.models import UserModel, Teacher, Course, BaseModel


class Post(BaseModel):
    class Meta:
        abstract = True

    author = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)
    amount_of_likes = models.IntegerField(default=0)
    headline = models.CharField(max_length=256)
    text = models.TextField()


class TeacherPost(Post):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    @classmethod
    def create(cls, author_name: str, headline: str, text: str, teacher: Teacher) -> 'TeacherPost':
        user = UserModel.get_user_by_user_name(author_name)
        if not user:
            return None
        post, created = TeacherPost.objects.get_or_create(author=user, headline=headline, text=text, Teacher=teacher)
        cls.log_created(cls.__name__, post.id, created)
        return post


class CoursePost(Post):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    @classmethod
    def create(cls, author_name: str, headline: str, text: str, course: Course) -> 'CoursePost':
        user = UserModel.get_user_by_user_name(author_name)
        if not user:
            return None
        post, created = CoursePost.objects.get_or_create(author=user, headline=headline, text=text, course=course)
        cls.log_created(cls.__name__, post.id, created)
        return post

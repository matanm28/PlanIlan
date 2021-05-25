import logging
import random

from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from polymorphic.models import PolymorphicModel

from ..decorators import receiver_subclasses
from . import Account, Teacher, Course, BaseModel, Rating


class Review(PolymorphicModel, BaseModel):
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    headline = models.CharField(max_length=80)
    text = models.TextField(max_length=5000)
    slug = models.SlugField(max_length=100, unique=True, editable=False, allow_unicode=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'

    def like_review(self, user: Account) -> 'Like':
        query = self.likes.filter(user=user)
        if not query.exsits():
            like = Like.create(user, self)
            return like
        return query.get()

    def remove_like(self, user: Account) -> bool:
        query = self.likes.filter(user=user)
        if query.exits():
            try:
                like = query.get()
                like.delete()
            except (MultipleObjectsReturned, models.Model.DoesNotExist):
                logging.exception(f"unable to delete like of user {user.username} from {type(self)} {self.pk}")
                return False
        return True

    @property
    def text_preview(self) -> str:
        text_length = len(self.text)
        return f'{self.text[:50]}...' if text_length > 50 else self.text[:text_length]

    def edit(self, edited_headline: str = None, edited_text: str = None, edited_rating: Rating = None, **kwargs) -> bool:
        edited_fields = (self.__edit_headline(edited_headline), self.__edit_text(edited_text), self.__edit_rating(edited_rating))
        return any(edited_fields)

    def __edit_headline(self, edited_headline: str) -> bool:
        if edited_headline is None:
            return False
        self.headline = edited_headline
        return True

    def __edit_text(self, edited_text: str) -> bool:
        if edited_text is None:
            return False
        self.text = edited_text
        return True

    def __edit_rating(self, edited_rating: Rating) -> bool:
        if edited_rating is None:
            return False
        self.rating.delete()
        self.rating = edited_rating
        return True

    def __str__(self) -> str:
        return f'{self.text_preview}'


class TeacherReview(Review):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='reviews')

    class Meta:
        db_table = 'teacher_reviews'


def upload_location(instance: 'CourseReview', filename: str, **kwargs):
    return f'review/course/{instance.course.name}/{instance.author.username}/{instance.pk}-{filename}'


class CourseReview(Review):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    image = models.ImageField(upload_to=upload_location, default='course_average-1.jpg', null=True, blank=True)
    is_image_valid = models.BooleanField(default=False)
    average = models.FloatField(null=True)

    class Meta:
        db_table = 'course_reviews'

    def get_image_url_if_valid(self):
        if not self.image or not self.is_image_valid:
            return None
        return self.image.url

    def edit(self, edited_headline: str = None, edited_text: str = None, edited_rating: Rating = None, **kwargs) -> bool:
        edit_made = super().edit(edited_headline, edited_text, edited_rating)
        if 'edited_image' in kwargs:
            edit_made = edit_made or self.__edit_image(kwargs['edited_image'])
        return edit_made

    def __edit_image(self, edited_image):
        if edited_image is None:
            return False
        self.image.delete()
        # something to save image
        return True


@receiver_subclasses(pre_save, Review, 'make_slug_for_review', weak=False)
def pre_save_review_receiver(sender, instance: Review, *args, **kwargs):
    if not instance.slug:
        if isinstance(instance, CourseReview):
            special_str_for_slug = instance.course.name
        elif isinstance(instance, TeacherReview):
            special_str_for_slug = instance.teacher.name
        else:
            special_str_for_slug = random.randint(0, 10 ** 5)
        instance.slug = slugify(f'{instance.author.username}-{special_str_for_slug}', allow_unicode=True)


@receiver(post_delete, sender=CourseReview, dispatch_uid='delete_image_from_files_when_review_is_deleted', weak=False)
def review_delete(sender, instance: CourseReview, **kwargs):
    instance.image.delete(False)


class Like(BaseModel):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='likes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = 'likes'

    def create(self, user: Account, review: Review) -> 'Like':
        like = Like.objects.create(user=user, review=review)
        logging.info(f'like on review {review.pk} from {user.username} created')
        return like

    def __str__(self):
        return f'{self.user.username} אהב את {self.review.slug}'


class Reply(BaseModel):
    text = models.TextField(max_length=2000)
    user = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='replies')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'replies'

    @classmethod
    def create(cls, text: str, user: Account, review: Review) -> 'BaseModel':
        reply = Reply.objects.create(text=text, user=user, review=review)
        logging.info(f'reply to review {review.pk} from user {user.username} created')
        return reply

    @property
    def preview(self) -> str:
        text_length = len(self.text)
        return f'{self.text[:50]}...' if text_length > 50 else self.text[:text_length]

    def edit(self, edited_text: str = None) -> bool:
        if edited_text is None:
            return False
        self.text = edited_text
        self.save()
        return True

    def __str__(self):
        return f'{self.preview} ({self.date_created.strftime("%d.%m.%y ב- %H:%M")})'

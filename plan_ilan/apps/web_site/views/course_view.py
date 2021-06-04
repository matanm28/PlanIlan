from django.core import serializers
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from plan_ilan.apps.web_site.models import *
from plan_ilan.apps.web_site.views import add_or_remove_like, save_comment_and_rating, delete_comment, \
    update_review_and_rating


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = "plan_ilan/course_detail.html"

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        course_rating = CourseRating.objects.filter(course=context['course'])
        course_reviews = CourseReview.objects.filter(course=context['course'])
        lessons = Lesson.objects.filter(course=context['course'])
        lessons_pk = list(map(lambda lesson: lesson.pk, lessons))
        teacher_list = [t.title_and_name for t in Teacher.objects.filter(lessons__pk__in=lessons_pk).distinct()]
        users_rated = [rev.author.user for rev in course_reviews]
        context['course_rating'] = course_rating
        context['course_reviews'] = course_reviews
        context['users_rated'] = users_rated
        context['lessons'] = lessons
        context['teacher_list'] = teacher_list
        return context

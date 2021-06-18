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

    def get_success_url(self):
        self.object = self.get_object()
        return reverse_lazy('course_detail', kwargs={'pk': self.object.pk}, )

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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST.get('action', '') == 'edit':
            update_review_and_rating(request)
        elif request.POST.get('PostID', ''):
            return JsonResponse(add_or_remove_like(request), safe=False)
        elif request.POST.get('Rating_object_ID', ''):
            save_comment_and_rating(request)
        return HttpResponseRedirect(reverse('course_detail', kwargs={'pk': self.object.pk}))

    def get(self, request, *args, **kwargs):
        if request.is_ajax() and request.user.is_authenticated:
            all_likes = Like.objects.filter(user=Account.objects.get(user=request.user))
            json_likes_list = serializers.serialize("json", all_likes)
            return JsonResponse({'json_likes_list': json_likes_list}, safe=False)
        else:
            return super(CourseDetailView, self).get(request, *args, **kwargs)

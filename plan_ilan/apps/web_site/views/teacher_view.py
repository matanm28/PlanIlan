from django.core import serializers
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from plan_ilan.apps.web_site.models import *
from plan_ilan.apps.web_site.views import add_or_remove_like, save_comment_and_rating, delete_comment, \
    update_review_and_rating


class TeacherDetailView(generic.DetailView):
    model = Teacher
    template_name = "plan_ilan/teacher_detail.html"

    def get_success_url(self):
        self.object = self.get_object()
        return reverse_lazy('teacher_detail', kwargs={'pk': self.object.pk}, )

    def get_context_data(self, **kwargs):
        context = super(TeacherDetailView, self).get_context_data(**kwargs)
        teacher_rating = TeacherRating.objects.filter(teacher=context['teacher'])
        teacher_reviews = TeacherReview.objects.filter(teacher=context['teacher'])
        users_rated = [rev.author.user for rev in teacher_reviews]
        context['teacher_rating'] = teacher_rating
        context['teacher_reviews'] = teacher_reviews
        context['users_rated'] = users_rated
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST.get('load_likes', '') and request.user.is_authenticated:
            all_likes = Like.objects.filter(user=Account.objects.get(user=request.user))
            json_likes_list = serializers.serialize("json", all_likes)
            return JsonResponse({'json_likes_list': json_likes_list}, safe=False)
        elif request.POST.get('action', '') == 'edit':
            update_review_and_rating(request)
        elif request.POST.get('PostID', ''):
            return JsonResponse(add_or_remove_like(request), safe=False)
        elif request.POST.get('Rating_object_ID', ''):
            save_comment_and_rating(request)
        return HttpResponseRedirect(reverse('teacher_detail', kwargs={'pk': self.object.pk}))

    def get(self, request, *args, **kwargs):
        return super(TeacherDetailView, self).get(request, *args, **kwargs)


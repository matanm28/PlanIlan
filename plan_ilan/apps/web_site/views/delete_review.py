from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from plan_ilan.apps.web_site.models import Review, TeacherReview, TeacherRating, CourseRating, Account


class ReviewDeleteView(generic.DeleteView):
    model = Review

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        account_user = Account.objects.filter(user=request.user)
        if isinstance(self.object, TeacherReview):
            rating_query = TeacherRating.objects.filter(user=account_user[0], teacher=self.object.teacher)
            id_to_transfer = self.object.teacher.pk
        else:
            rating_query = CourseRating.objects.filter(user=account_user[0], course=self.object.course)
            id_to_transfer = self.object.course.code
        self.object.delete()
        if rating_query.exists():
            rating = rating_query.get()
            rating.delete()
        return HttpResponseRedirect(reverse_lazy('teacher_detail', kwargs={'pk': id_to_transfer}, ))

from django.urls import reverse_lazy
from django.views import generic

from plan_ilan.apps.web_site.models import Review, TeacherReview, TeacherRating, Rating, CourseRating, CourseReview


class ReviewDeleteView(generic.DeleteView):
    model = Review

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if isinstance(self.object, TeacherReview):
            rating = TeacherRating.objects.filter(user=request.user, teacher=self.object.teacher)
            id_to_transfer = self.object.teacher.pk
        else:
            rating = CourseRating.objects.filter(user=request.user, course=self.object.course)
            id_to_transfer = self.object.course.code
        self.object.delete()
        rating.delete()
        return reverse_lazy('teacher_detail', kwargs={'pk': id_to_transfer}, )


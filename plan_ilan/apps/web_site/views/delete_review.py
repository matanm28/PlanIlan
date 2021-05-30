from django.urls import reverse_lazy
from django.views import generic

from plan_ilan.apps.web_site.models import Review


class ReviewDeleteView(generic.DeleteView):
    model = Review

    def get_success_url(self):
        self.object = self.get_object()
        return reverse_lazy('teacher_detail', kwargs={'pk': self.object.pk}, )

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)
from django.urls import include, path
from rest_framework import routers
from rest_framework.views import APIView

from . import views
from plan_ilan import settings


class Router(routers.DefaultRouter):
    include_root_view = True
    include_format_suffixes = False
    root_view_name = 'index'

    def get_api_root_view(self, api_urls=None):
        return views.PlanIlanRootView.as_view([view_set_class for _, view_set_class, _ in self.registry])


router = Router()

router.register(r'courses', views.CourseViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'lesson-times', views.LessonTimeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

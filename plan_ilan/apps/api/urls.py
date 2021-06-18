from django.urls import include, path
from rest_framework import routers

from . import views


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

# default_router = routers.DefaultRouter()
# default_router.register(r'timetables', views.TimetableViewSet)
# default_router.register(r'blocked_time_periods', views.BlockedTimePeriodViewSet)
# default_router.register(r'ranked_lessons', views.RankedLessonViewSet)
# default_router.register(r'time_intervals', views.TimeIntervalViewSet)
# default_router.register(r'intervals', views.IntervalViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('', include(default_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

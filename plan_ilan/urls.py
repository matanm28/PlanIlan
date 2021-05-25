"""plan_ilan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import settings
from .apps.web_site import views

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', views.home, name='home'),
                  path('search/', views.search, name='search'),
                  path('timetable/', views.time_table, name='timetable'),
                  # USER AUTHENTICATION URLS
                  path('login/', views.login_page, name='login'),
                  path('logout/', views.logout_user, name='logout'),
                  path('register/', views.register, name='register'),
                  # RESET PASSWORD URLS
                  path('reset_password/',
                       auth_views.PasswordResetView.as_view(template_name="plan_ilan/password_reset.html"),
                       name='reset_password'),
                  path('reset_password_sent/',
                       auth_views.PasswordResetDoneView.as_view(template_name="plan_ilan/password_reset_sent.html"),
                       name='password_reset_done'),
                  path('reset/<uidb64>/<token>/',
                       auth_views.PasswordResetConfirmView.as_view(template_name="plan_ilan/password_reset_form.html"),
                       name='password_reset_confirm'),
                  path('reset_password_complete/',
                       auth_views.PasswordResetCompleteView.as_view(template_name="plan_ilan/password_reset_done.html"),
                       name='password_reset_complete'),
                  path('api/', include('plan_ilan.apps.api.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)), ]

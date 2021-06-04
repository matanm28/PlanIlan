from django.contrib.auth import views as auth_views
from django.urls import path

from plan_ilan.apps.web_site import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    # USER AUTHENTICATION URLS
    path('login/', views.login_page, name='login'),
    path('about/', views.about_page, name='about'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('teacher/<int:pk>',
         views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('course/<int:pk>',
         views.CourseDetailView.as_view(), name='course_detail'),
    path('delete-review/<int:pk>',
         views.ReviewDeleteView.as_view(), name='delete_review'),
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
]

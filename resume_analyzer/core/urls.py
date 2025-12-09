# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("upload/", views.upload_resume, name="upload_resume"),
    path("analyze/", views.analyze, name="analyze"),
    path("analyze/<int:resume_id>/", views.analyze, name="analyze_with_resume"),
    path("result/<int:analysis_id>/", views.analysis_result, name="analysis_result"),
    path("send_email/<int:analysis_id>/", views.send_email, name="send_email"),
]

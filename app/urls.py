from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("student/", views.student_page, name="student_page"),
]

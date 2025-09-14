from django.urls import path
from dashboard_api import views

urlpatterns = [
    path("data/", views.dashboard_data, name="dashboard_data"),
]

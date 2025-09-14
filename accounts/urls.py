from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.school_admin_register, name="school_admin_register"),
    path("login/", views.school_admin_login, name="school_admin_login"),
    path("logout/", views.logout_view, name="logout_view"),
    # forgot password
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("otp-confirmation/", views.otp_confirmation, name="otp_confirmation"),
    path(
        "set-new-password/<int:user_id>/",
        views.set_new_password,
        name="set_new_password",
    ),
]

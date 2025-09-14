from django.shortcuts import render, redirect
from .forms import SchoolAdminRegisterForm, SchoolAdminLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .utils import is_email_valid, forgot_password_email
from .models import OTP, CustomUser
from django.contrib.auth.password_validation import validate_password


def school_admin_register(request):
    if request.method == "POST":
        form = SchoolAdminRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("accounts:school_admin_login")

        context = {"form": form}
        return render(request, "accounts/register.html", context)

    form = SchoolAdminRegisterForm()
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def school_admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("app:dashboard")

        messages.error(request, "Invalid username or password")
        return redirect("accounts:school_admin_login")

    form = SchoolAdminLoginForm()

    context = {"form": form}
    return render(request, "accounts/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("accounts:school_admin_login")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not is_email_valid(email):
            messages.error(request, "Enter a valid email")
            return redirect("accounts:forgot_password")

        try:
            forgot_password_email(email)
        except Exception as e:
            messages.error(request, str(e))
            return redirect("accounts:forgot_password")

        print(email, "Email sent successfully")
        messages.success(request, "Email sent successfully. Please check your inbox")
        return redirect("accounts:otp_confirmation")

    return render(request, "accounts/forgot-password.html")


def otp_confirmation(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user_id = OTP.check_otp(otp)
        if user_id is None:
            messages.error(request, "Invalid OTP, please try again")
            return redirect("accounts:otp_confirmation")

        return redirect("accounts:set_new_password", user_id=user_id)

    return render(request, "accounts/otp-confirmation.html")


def set_new_password(request, user_id=None):
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("accounts:set_new_password")

        try:
            validate_password(password1)
        except Exception as e:
            for error in list(e):
                messages.error(request, str(error))
            return redirect("accounts:set_new_password")
        else:
            if user_id is not None:
                user = CustomUser.objects.filter(id=user_id).first()
                if user is None:
                    messages.error(request, "User does not exist")
                    return redirect("accounts:set_new_password")

            user.set_password(password1)
            user.save()
            messages.success(request, "Password changed successfully")
            return redirect("accounts:school_admin_login")

    return render(request, "accounts/new-password.html")

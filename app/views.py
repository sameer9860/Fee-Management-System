
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from school.forms import SchoolForm
from django.urls import reverse_lazy
from accounts.models import CustomUser


@login_required
def dashboard(request):
    try:
        request.user.school
    except Exception as e:
        if request.user.role == CustomUser.Roles.STUDENT:
            return redirect("app:student_page")

        print(e)
        # message to welcome user and direct them to school registration
        message = (
            "Welcome to the dashboard! Please register your school to get started."
        )
        messages.info(request, message)

        school_res_form = SchoolForm()
        form_submission_url = reverse_lazy("school:school_register")
        context = {"form": school_res_form, "form_submission_url": form_submission_url}
        return render(request, "app/dashboard.html", context)

    return render(request, "app/dashboard.html")


def student_page(request):
    return render(request, "app/student-page.html")

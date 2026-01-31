
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


from django.db import models
from payment.models import Payment
from school.models import Grade


@login_required
def student_page(request):
    # Ensure only students access this page
    if request.user.role != CustomUser.Roles.STUDENT:
        return redirect("app:dashboard")

    student = request.user

    # Payments
    recent_payments = student.payments.order_by("-updated_at")[:6]
    total_paid = student.payments.filter(status=Payment.Status.SUCCESS).aggregate(total=models.Sum("amount"))["total"]
    total_paid = total_paid or 0

    # Fee summary for grade
    fee_info = None
    due_amount = None
    if student.grade:
        fee_info = Grade.get_total_fees(student.grade)
        grand_total = fee_info["grand_total"]
        due_amount = grand_total - total_paid

    context = {
        "student": student,
        "recent_payments": recent_payments,
        "total_paid": total_paid,
        "fee_info": fee_info,
        "due_amount": due_amount,
    }

    return render(request, "app/student-page.html", context)

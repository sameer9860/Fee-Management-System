from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_GET, require_POST

from accounts.models import CustomUser
from school.forms import (
    FeeForm,
    GradeForm,
    SchoolForm,
    StudentBulkRegisterForm,
    StudentRegistrationForm,
)
from school.models import Fee, Grade, TempCSVFile
from school.background_tasks import bulk_create_students_from_csv
from school.filters import StudentFilter
from django.core.paginator import Paginator


@require_POST
def school_register(request):
    form_data = request.POST
    form = SchoolForm(form_data, request.FILES, request=request)
    if form.is_valid():
        form.save()
        return redirect("school:school_profile")

    return render(request, "app/dashboard.html", {"form": form})


@require_GET
@login_required
def school_profile(request):
    school_admin = request.user
    print(school_admin.profile_pic)
    try:
        school_data = school_admin.school
    except Exception as e:
        print(e)
        return redirect("app:dashboard")

    context = {"admin": school_admin, "school": school_data}
    return render(request, "school/profile.html", context)


@login_required
def school_update(request):
    if request.method == "POST":
        form_data = request.POST
        form = SchoolForm(
            form_data, request.FILES, instance=request.user.school, request=request
        )
        if form.is_valid():
            form.save()
            return redirect("school:school_profile")

    form = SchoolForm(instance=request.user.school, request=request)
    form_submission_url = reverse_lazy("school:school_update")

    context = {"form": form, "form_submission_url": form_submission_url}

    return render(request, "school/update-school-info.html", context)


def grade(request):
    if request.method == "POST":
        form = GradeForm(request.POST, request=request)
        if form.is_valid():
            try:
                saved_grade = form.save()
            except IntegrityError:
                return JsonResponse(
                    {"success": False, "message": "Grade already exists."}
                )
            else:
                saved_grade_dict = {"id": saved_grade.id, "name": saved_grade.name}
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Grade added successfully.",
                        "data": saved_grade_dict,
                    }
                )

    form = GradeForm()
    grades_list = request.user.school.classes.all()

    context = {"form": form, "grades_list": grades_list}

    return render(request, "school/grade-create-form.html", context)


def grade_delete(request, pk):
    try:
        Grade.objects.get(id=pk).delete()
    except Grade.DoesNotExist:
        return JsonResponse({"success": False, "message": "Grade doesn't exist."})
    else:
        return JsonResponse({"success": True, "message": "Grade deleted successfully."})


def grade_update(request, pk):
    try:
        grade = Grade.objects.get(pk=pk)
    except Grade.DoesNotExist:
        messages.error(request, "Grade does not exist")
        return redirect("school:grade")

    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, "Grade updated successfully")
            return redirect("school:grade")

        messages.error(request, "Failed to update grade")
        return redirect("school:grade")

    else:
        form = GradeForm(instance=grade, request=request)
        context = {"form": form}
        return render(request, "school/grade-update-form.html", context)


def fee(request):
    if request.method == "POST":
        grade_id = request.POST.get("grade_id")
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return JsonResponse({"success": False, "message": "Grade does not exist."})

        form = FeeForm(request.POST)
        if form.is_valid():
            try:
                saved_fee = form.save(grade=grade)
            except IntegrityError:
                return JsonResponse(
                    {"success": False, "message": "Fee already exists."}
                )

            reponse = {
                "success": True,
                "message": "Fee added successfully.",
                "data": {
                    "id": saved_fee.id,
                    "name": saved_fee.name,
                    "amount": saved_fee.amount,
                },
            }
            return JsonResponse(reponse)

    grade_id = request.GET.get("grade_id")
    try:
        grade = Grade.objects.get(id=grade_id)
        fees = grade.fees.all()
    except Grade.DoesNotExist:
        messages.error(request, "Grade does not exist")
        return redirect("school:grade")

    form = FeeForm()
    context = {"form": form, "grade": grade, "fees": fees}
    return render(request, "school/fee-create.html", context)


def fee_delete(request, pk):
    try:
        Fee.objects.get(id=pk).delete()
    except Fee.DoesNotExist:
        return JsonResponse({"success": False, "message": "Fee doesn't exist."})
    else:
        return JsonResponse({"success": True, "message": "Fee deleted successfully."})


def fee_update(request, pk):
    try:
        fee = Fee.objects.get(pk=pk)
        base_url = reverse("school:fee")
        query_string = urlencode({"grade_id": fee.grade.id})
        url = f"{base_url}?{query_string}"
    except Fee.DoesNotExist:
        messages.error(request, "fee does not exist")
        return redirect(url)

    if request.method == "POST":
        form = FeeForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, "fee updated successfully")
            return redirect(url)

        messages.error(request, "Failed to update fee")
        return redirect(url)

    else:
        form = FeeForm(instance=fee)
        context = {"form": form}
        return render(request, "school/fee-update.html", context)


def students(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, "Student registered successfully!")
            return redirect("student_register")
    else:
        form = StudentRegistrationForm(request=request)
        csv_form = StudentBulkRegisterForm(request=request)

    all_students = CustomUser.objects.filter(
        role=CustomUser.Roles.STUDENT,
        grade__isnull=False,
        grade__school=request.user.school,
    )
    filtered_students = StudentFilter(request.GET, queryset=all_students)

    paginator = Paginator(
        filtered_students.qs, 10
    )  # Show 10 students records per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "form": form,
        "students": filtered_students.qs,
        "csv_form": csv_form,
        "filter_form": filtered_students.form,
        "page_obj": page_obj,
    }

    return render(request, "school/students.html", context)


def upload_students_csv(request):
    if request.method == "POST":
        form = StudentBulkRegisterForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            saved_file = TempCSVFile.objects.create(file=request.FILES["csv_file"])
            bulk_create_students_from_csv(
                saved_file.id, request.POST.get("grade", None)
            )
            messages.success(request, "Students registered successfully!")
            return redirect("school:students")

    return redirect("school:students")

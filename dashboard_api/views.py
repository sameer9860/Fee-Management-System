from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.models import CustomUser
from payment.models import Payment
from school.models import Grade
from django.db import models
from dashboard_api.utils import get_payment_chart_data


@api_view(["GET"])
def dashboard_data(request):
    total_students_school = CustomUser.objects.filter(
        role=CustomUser.Roles.STUDENT, grade__school=request.user.school
    ).count()
    total_payment_amount = Payment.objects.filter(
        student__grade__school=request.user.school, status=Payment.Status.SUCCESS
    ).aggregate(total_amount=models.Sum("amount"))["total_amount"]

    grades = request.user.school.classes.all()
    all_grades_fee = 0
    for grade in grades:
        no_of_students = grade.students.count()
        grade_total_fee = Grade.get_total_fees(grade).get("grand_total", 0)
        all_grades_fee += grade_total_fee * no_of_students

    pending_payment_amount = all_grades_fee - total_payment_amount

    active_classes = Grade.objects.filter(school=request.user.school).count()

    chart_data = get_payment_chart_data(request.user)
    chart = {
        "labels": chart_data["labels"],
        "datasets": chart_data["datasets"],
    }

    data = {
        "total_students_school": total_students_school,
        "total_payments": total_payment_amount,
        "pending_payment_amount": pending_payment_amount,
        "active_classes": active_classes,
        "chart": chart,
    }

    return Response(data)

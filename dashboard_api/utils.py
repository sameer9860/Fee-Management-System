from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
import calendar
from payment.models import Payment


def get_payment_chart_data(user):
    # current year
    year = timezone.now().year
    # filter payments with success status
    # filter only payments for the current year
    # annotate each payment with the month it was made
    # group the payments by month
    # calculate the total amount of payments for each month
    # order the results by month
    qs = (
        Payment.objects.filter(
            student__grade__school=user.school,
            status=Payment.Status.SUCCESS,
            created_at__year=year,  # filter only current year
        )
        .annotate(month=TruncMonth("created_at"))  # 2025-01-01 # 2025-02-01
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    labels = [calendar.month_abbr[item["month"].month] for item in qs]
    data = [item["total"] for item in qs]

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Payments Received (₹)",
                "data": data,
                "backgroundColor": "#22c55e",  # Tailwind green-500
            }
        ],
    }

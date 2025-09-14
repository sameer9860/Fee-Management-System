
# Register your models here.
from django.contrib import admin
from payment.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "amount",
        "status",
        "created_at",
        "updated_at",
        "student",

        # Khalti fields
        "initial_khalti_id",
        "khalti_status",
        "khalti_transaction_id",

        # eSewa fields
        "esewa_status",
        "esewa_reference_id",
        "esewa_order_id",
    ]

    list_filter = [
        "status",
        "gateway",
        "khalti_status",
        "esewa_status",
        "created_at",
    ]

    search_fields = [
        "student__username",
        "student__email",
        "khalti_transaction_id",
        "esewa_reference_id",
        "esewa_order_id",
    ]


admin.site.register(Payment, PaymentAdmin)

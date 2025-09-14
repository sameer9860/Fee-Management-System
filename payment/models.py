# payment/models.py
from django.db import models
import uuid

class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED = "INITIATED", "Initiated"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        PENDING = "PENDING", "Pending"

    class Gateway(models.TextChoices):
        KHALTI = "KHALTI", "Khalti"
        ESEWA = "ESEWA", "eSewa"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    student = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    name = models.CharField(max_length=150, blank=True)

    gateway = models.CharField(
        max_length=20, choices=Gateway.choices, default=Gateway.KHALTI
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.INITIATED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Khalti fields (keep same)
    initial_khalti_id = models.CharField(max_length=255, null=True, blank=True, editable=False)
    khalti_status = models.CharField(max_length=50, null=True, blank=True, editable=False)
    khalti_transaction_id = models.CharField(max_length=255, null=True, blank=True, editable=False)

    # eSewa fields (new)
    esewa_status = models.CharField(max_length=50, null=True, blank=True, editable=False)
    esewa_reference_id = models.CharField(max_length=255, null=True, blank=True, editable=False)
    esewa_order_id = models.CharField(max_length=255, null=True, blank=True, editable=False)

    def __str__(self):
        return f"{self.gateway} - {self.name} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.name:
            previous_count = Payment.objects.filter(
                student=self.student, status=Payment.Status.SUCCESS
            ).count()
            self.name = f"Installment {previous_count + 1}"
        super().save(*args, **kwargs)

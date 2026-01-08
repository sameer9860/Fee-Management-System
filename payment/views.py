from django.shortcuts import render, redirect
from school.models import Fee, Grade
from django.db import models
from django.views.decorators.http import require_POST
import requests
import json
from django.urls import reverse
from payment.models import Payment
from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404


def transactions(request):
    transactions = request.user.payments.all().order_by("-updated_at")

    context = {"transactions": transactions}

    return render(request, "payment/transactions.html", context)


def due_payments(request):
    grade_fee = Grade.get_total_fees(request.user.grade)
    previous_payment_total = request.user.payments.filter(
        status=Payment.Status.SUCCESS
    ).aggregate(grand_total=models.Sum("amount"))
    if previous_payment_total["grand_total"] is None:
        due_fee = grade_fee["grand_total"]
    else:
        due_fee = grade_fee["grand_total"] - previous_payment_total["grand_total"]

    context = {
        "grade_fee": grade_fee["grand_total"],
        "fee_structure": grade_fee["fee_structure_description"],
        "due_fee": due_fee,
    }

    return render(request, "payment/due-payments.html", context)


@require_POST
def payment(request):
    try:
        new_payment = Payment.objects.create(
            student=request.user,
            amount=request.POST.get("amount")
        )
    except Exception as e:
        print(e)
        return redirect("payment:due_payments")

    return redirect("payment:choose_gateway", payment_id=new_payment.id)


def choose_gateway(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return render(request, "payment/choose_gateway.html", {"payment": payment})


@require_POST
def payment_khalti(request):
    payment_id = request.POST.get("payment_id")
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    payment.gateway = Payment.Gateway.KHALTI
    payment.save()

    # initiate Khalti request
    url = f"{settings.KHALTI_BASE_URL}{settings.KHALTI_INITIATE_URL}"

    payload = json.dumps(
        {
            "return_url": request.build_absolute_uri(reverse("payment:payment_done")),
            "website_url": request.build_absolute_uri("/"),
            "amount": f"{int(float(payment.amount) * 100)}",  # in paisa
            "purchase_order_id": str(payment.id),
            "purchase_order_name": payment.name,
            "customer_info": {
                "name": f"{request.user.first_name} {request.user.last_name}",
                "email": request.user.email,
                "phone": request.user.phone_number,
            },
        }
    )

    headers = {
        "Authorization": f"key {settings.KHALTI_SECRET}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        return redirect(response.json()["payment_url"])
    else:
        messages.error(request, "Failed to initiate Khalti payment")
        return redirect("payment:due_payments")



def payment_done(request):
    query_params = request.GET
    payment_id = query_params.get("purchase_order_id")
    initial_payment_id = query_params.get("pidx")

    if not payment_id or not initial_payment_id:
        messages.error(request, "Invalid payment callback")
        return redirect("payment:due_payments")

    # Verify payment with Khalti
    verification_url = f"{settings.KHALTI_BASE_URL}{settings.KHALTI_LOOKUP_URL}"
    payload = json.dumps({"pidx": initial_payment_id})
    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET}",
        "Content-Type": "application/json",
    }

    response = requests.post(verification_url, headers=headers, data=payload)
    result = response.json()

    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        messages.error(request, "Payment details not found")
        return redirect("payment:due_payments")

    if response.status_code == 200:
        # Check amount integrity
        if (payment.amount * 100) == result.get("total_amount"):
            if result.get("status") == "Completed":
                payment.status = Payment.Status.SUCCESS
            elif result.get("status") in ("Expired", "Failed", "User canceled"):
                payment.status = Payment.Status.FAILED
            else:
                payment.status = Payment.Status.PENDING

            payment.khalti_status = result.get("status")
            payment.khalti_transaction_id = result.get("transaction_id")
            payment.initial_khalti_id = result.get("pidx")
            payment.save()
        else:
            messages.error(request, "Payment amount verification failed")
            return redirect("payment:due_payments")
    else:
        messages.error(request, "Payment verification failed")
        payment.status = Payment.Status.FAILED
        payment.save()
        return redirect("payment:due_payments")

    return redirect("payment:transactions")


@require_POST
def payment_esewa(request):
    payment_id = request.POST.get("payment_id")
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    payment.gateway = Payment.Gateway.ESEWA
    payment.save()

    context = {
        "payment": payment,
        "esewa_url": settings.ESEWA_BASE_URL,   # uat.esewa.com.np/epay/main
        "merchant_code": settings.ESEWA_MERCHANT_CODE,
        "success_url": request.build_absolute_uri(reverse("payment:esewa_verify")),
        "failure_url": request.build_absolute_uri(reverse("payment:due_payments")),
    }
    return render(request, "payment/esewa_redirect.html", context)

def esewa_verify(request):
    oid = request.GET.get("oid")  # our Payment.id
    amt = request.GET.get("amt")
    refId = request.GET.get("refId")

    try:
        payment = Payment.objects.get(id=oid, gateway=Payment.Gateway.ESEWA)
    except Payment.DoesNotExist:
        messages.error(request, "Payment not found")
        return redirect("payment:due_payments")

    payload = {
        "amt": amt,
        "scd": settings.ESEWA_MERCHANT_CODE,
        "pid": oid,
        "rid": refId,
    }

    response = requests.post(settings.ESEWA_VERIFY_URL, data=payload)

    if response.ok and "Success" in response.text:
        payment.status = Payment.Status.SUCCESS
        payment.esewa_status = "Completed"
        payment.esewa_reference_id = refId
        payment.esewa_order_id = oid
        payment.save()
        return redirect("payment:transactions")
    else:
        payment.status = Payment.Status.FAILED
        payment.esewa_status = "Failed"
        payment.save()
        messages.error(request, "eSewa verification failed")
        return redirect("payment:due_payments")

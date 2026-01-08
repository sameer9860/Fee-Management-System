# payment/urls.py
from django.urls import path
from payment import views

app_name = "payment"

urlpatterns = [
    path("transactions/", views.transactions, name="transactions"),
    path("due-payments/", views.due_payments, name="due_payments"),
    path("payment/", views.payment, name="payment"),
    path("payment/choose/<uuid:payment_id>/", views.choose_gateway, name="choose_gateway"),
    path("payment/khalti/", views.payment_khalti, name="payment_khalti"),
    path("payment/esewa/", views.payment_esewa, name="payment_esewa"),
    path("payment/done/", views.payment_done, name="payment_done"),
    path("payment/esewa/verify/", views.esewa_verify, name="esewa_verify"),
]

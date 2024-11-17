from django.urls import path
from apps.payments.views import (
    rent_payments,
    mealcard_payments,
    new_rent_payment,
    new_mealcard_payment,
)

urlpatterns = [
    path("rent-payments/", rent_payments, name="rent-payments"),
    path("meal-card-payments/", mealcard_payments, name="meal-card-payments"),
    path("new-rent-payment/", new_rent_payment, name="new-rent-payment"),
    path("new-mealcard-payment/", new_mealcard_payment, name="new-mealcard-payment"),
]

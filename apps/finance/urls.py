from django.urls import path
from apps.finance.views import LibraryFinePaymentListView, capture_library_fine_payment

urlpatterns = [
    path("library-fines/", LibraryFinePaymentListView.as_view(), name="library-fines"),
    path(
        "capture-library-fine-payment/",
        capture_library_fine_payment,
        name="capture-library-fine-payment",
    ),
]

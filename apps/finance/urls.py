from django.urls import path
from apps.finance.views import finance_home, BudgetsListView, LibraryFinePaymentListView, capture_library_fine_payment

urlpatterns = [
    path("", finance_home, name="finance-home"),
    path("budgets/", BudgetsListView.as_view(), name="budgets"),
    path("library-fines/", LibraryFinePaymentListView.as_view(), name="library-fines"),
    path(
        "capture-library-fine-payment/",
        capture_library_fine_payment,
        name="capture-library-fine-payment",
    ),
]

from django.urls import path
from apps.finance.views import LibraryFinePaymentListView, capture_library_fine_payment

from apps.finance.fees_structures.views import (
    FeesStructuresProgrammesListView,
    FeeStructureListView,
    new_fees_structure,
    edit_fees_structure,
    delete_fees_structure,
)


urlpatterns = [
    path("library-fines/", LibraryFinePaymentListView.as_view(), name="library-fines"),
    path(
        "capture-library-fine-payment/",
        capture_library_fine_payment,
        name="capture-library-fine-payment",
    ),
    path(
        "programmes-fees/",
        FeesStructuresProgrammesListView.as_view(),
        name="programmes-fees",
    ),
    path(
        "fees-structures/<int:programme_id>/",
        FeeStructureListView.as_view(),
        name="fees-structures",
    ),
]

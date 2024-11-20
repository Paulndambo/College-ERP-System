from django.urls import path
from apps.finance.views import (
    LibraryFinePaymentListView
)

urlpatterns = [
    path("library-fines/", LibraryFinePaymentListView.as_view(), name="library-fines"),
]
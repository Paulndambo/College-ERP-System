from django.urls import path
from .views import (
    VendorListCreateView,
    PurchaseOrderListCreateView,
    GoodsReceivedCreateView,
    VendorPaymentListCreateView
)

urlpatterns = [
    path("vendors/", VendorListCreateView.as_view()),
    path("purchase-orders/", PurchaseOrderListCreateView.as_view()),
    path("goods-received/", GoodsReceivedCreateView.as_view()),
    path("vendor-payments/", VendorPaymentListCreateView.as_view()),
]

from django.urls import path
from .views import (
    AwardedTendersAPIView,
    ReopenTenderView,
    TenderApplicationDocumentListCreateView,
    ApproveRejectTenderApplicationView,
    TenderApplicationDetailsAPIView,
    TenderApplicationDocumentsDetailsAPIView,
    TenderApplicationListCreateView,
    TenderListCreateAPIView,
    VendorDetailView,
    VendorListView,
    PurchaseOrderListCreateView,
    GoodsReceivedCreateView,
    VendorPaymentCreateAPIView,
    VendorPaymentsAPIView,
)

urlpatterns = [
    path("tenders/", TenderListCreateAPIView.as_view(), name="tender-list-create"),
    path("tender-applications/", TenderApplicationListCreateView.as_view(), name="tender-application-list-create"),
    path("awarded-tenders/", AwardedTendersAPIView.as_view(), name="awardd-tenders"),
    path("tender-application-documents/", TenderApplicationDocumentListCreateView.as_view(), name="application-document-create"),
    path("tender-application-documents/<int:pk>/", TenderApplicationDocumentsDetailsAPIView.as_view(), name="application-document-delete"),
    path("tender-applications/<int:pk>/review/", ApproveRejectTenderApplicationView.as_view(), name="review-tender-application"),
    path("tenders/<int:pk>/reopen/", ReopenTenderView.as_view(), name="reopen-tender"),
    path("tender-applications/<int:pk>/details/", TenderApplicationDetailsAPIView.as_view(), name="tender-application-details"),
    
    path("vendors/", VendorListView.as_view(), name="vendor-list"),
    path("vendors/<int:pk>/", VendorDetailView.as_view(), name="vendor-detail"),
    path("purchase-orders/", PurchaseOrderListCreateView.as_view(), name="purchase-order-list"),
    path("goods-received/receive/", GoodsReceivedCreateView.as_view(), name="goods-received"),
    path("vendor-payments/create/", VendorPaymentCreateAPIView.as_view(), name="vendor-payment-create"),
    path("vendor-payments/", VendorPaymentsAPIView.as_view(), name="vendor-payment-list"),
]

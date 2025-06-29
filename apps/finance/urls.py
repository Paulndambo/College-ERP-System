from django.urls import path
from apps.finance.library.views import ProcessLibraryPaymentView
from .views import (
    FeeStructureItemByStructureView,
    FeeStructureListView,
    FeeStructureRetrieveView,
    FeeStructureCreateView,
    FeeStructureUpdateView,
    FeeStructureDeleteView,
    FeeStructureItemListView,
    FeeStructureItemRetrieveView,
    FeeStructureItemCreateView,
    FeeStructureItemUpdateView,
    FeeStructureItemDeleteView,
)

urlpatterns = [
    # Pay library fines
    path(
        "library/process-payment/",
        ProcessLibraryPaymentView.as_view(),
        name="library-process-payment",
    ),
    
    # FeeStructure
    path("fee-structures/", FeeStructureListView.as_view(), name="fee-structure-list"),
    path(
        "fee-structures/create/",
        FeeStructureCreateView.as_view(),
        name="fee-structure-create",
    ),
    path(
        "fee-structures/<int:id>/",
        FeeStructureRetrieveView.as_view(),
        name="fee-structure-detail",
    ),
    path(
        "fee-structures/<int:id>/update/",
        FeeStructureUpdateView.as_view(),
        name="fee-structure-update",
    ),
    path(
        "fee-structures/<int:id>/delete/",
        FeeStructureDeleteView.as_view(),
        name="fee-structure-delete",
    ),
    # FeeStructureItem
    path(
        "fee-structure-items/", FeeStructureItemListView.as_view(), name="fee-item-list"
    ),
    path(
        "fee-structure-items/create/",
        FeeStructureItemCreateView.as_view(),
        name="fee-item-create",
    ),
    path(
        "fee-structure-items/<int:id>/",
        FeeStructureItemRetrieveView.as_view(),
        name="fee-item-detail",
    ),
    # urls.py
    path(
        "fee-structures/<int:fee_structure_id>/items/",
        FeeStructureItemByStructureView.as_view(),
        name="fee-structure-items-by-structure",
    ),
    path(
        "fee-structure-items/<int:id>/update/",
        FeeStructureItemUpdateView.as_view(),
        name="fee-item-update",
    ),
    path(
        "fee-structure-items/<int:id>/delete/",
        FeeStructureItemDeleteView.as_view(),
        name="fee-item-delete",
    ),
]

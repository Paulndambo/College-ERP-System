from rest_framework import generics, permissions
from django.db import transaction
from apps.accounting.models import Account
from django.shortcuts import get_object_or_404
from apps.accounting.services.journals import create_journal_entry
from apps.procurement.filters import OrderFilter, VendorFilter
from apps.procurement.utils import (
    generate_order_no,
    generate_payment_reference,
    generate_unique_vendor_no,
)
from apps.procurement.vendorPaymentMixin import VendorPaymentService
from .models import (
    ApplicationDocument,
    PurchaseItemReceipt,
    Tender,
    TenderApplication,
    TenderAward,
    Vendor,
    PurchaseOrder,
    GoodsReceived,
    VendorDocument,
    VendorPayment,
)
from .serializers import (
    PurchaseOrderCreateSerializer,
    PurchaseOrderListSerializer,
    TenderApplicationDocumentCreateSerializer,
    TenderApplicationDocumentListSerializer,
    TenderApplicationCreateUpdateSerializer,
    TenderApplicationListSerializer,
    TenderAwardSerializer,
    TenderCreateUpdateSerializer,
    TenderListSerializer,
    VendorListSerializer,
    GoodsReceivedSerializer,
    VendorPaymentCreateSerializer,
    VendorPaymentListSerializer,
)
from rest_framework.pagination import PageNumberPagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


class TenderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Tender.objects.all().order_by("-created_on")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TenderCreateUpdateSerializer
        return TenderListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AwardedTendersAPIView(generics.ListAPIView):
    queryset = TenderAward.objects.all().order_by("-created_on")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TenderAwardSerializer

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            qs = self.filter_queryset(qs)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_qs = paginator.paginate_queryset(qs, request)
                serializer = self.get_serializer(paginated_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


class TenderApplicationListCreateView(generics.ListCreateAPIView):
    queryset = TenderApplication.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TenderApplicationCreateUpdateSerializer
        return TenderApplicationListSerializer


class TenderApplicationDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TenderApplication.objects.all()
    serializer_class = TenderApplicationListSerializer
    lookup_field = "pk"
    http_method_names = ["get", "patch", "put", "delete"]


class TenderApplicationDocumentListCreateView(generics.ListCreateAPIView):
    queryset = ApplicationDocument.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TenderApplicationDocumentCreateSerializer
        return TenderApplicationDocumentListSerializer


class TenderApplicationDocumentsDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ApplicationDocument.objects.all()
    serializer_class = TenderApplicationDocumentCreateSerializer
    lookup_field = "pk"
    http_method_names = ["get", "patch", "put", "delete"]


class ApproveRejectTenderApplicationView(APIView):
    def patch(self, request, *args, **kwargs):
        application_id = kwargs.get("pk")
        action = request.data.get("status")

        try:
            application = TenderApplication.objects.get(pk=application_id)
        except TenderApplication.DoesNotExist:
            return Response(
                {"error": "Tender application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if action == "pending":
            application.status = "pending"
            application.save()
            return Response(
                {"message": "Application submitted for review successfully."},
                status=status.HTTP_200_OK,
            )
        if application.status != "pending":
            return Response(
                {"error": "Only pending applications can be approved or rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "rejected":
            application.status = "rejected"
            application.reviewed_by = request.user
            application.reviewed_on = timezone.now()
            application.save()
            return Response(
                {"message": "Tender application rejected successfully."},
                status=status.HTTP_200_OK,
            )

        with transaction.atomic():
            vendor = None

            if application.vendor_no:
                vendor = Vendor.objects.filter(vendor_no=application.vendor_no).first()

            if not vendor:
                vendor = Vendor.objects.filter(
                    Q(
                        company_registration_number=application.company_registration_number
                    )
                    | Q(tax_pin=application.tax_pin)
                ).first()

            if not vendor:
                generated_vendor_no = generate_unique_vendor_no()
                vendor = Vendor.objects.create(
                    name=application.company_name,
                    company_registration_number=application.company_registration_number,
                    tax_pin=application.tax_pin,
                    business_type=application.business_type,
                    contact_person=application.contact_person,
                    contact_person_phone=application.contact_person_phone,
                    contact_person_email=application.contact_person_email,
                    phone=application.phone,
                    email=application.email,
                    address=application.address,
                    vendor_no=generated_vendor_no,
                    # registered_by=self.request.user
                )

            for doc in application.documents.all():
                VendorDocument.objects.create(
                    vendor=vendor,
                    document_name=doc.document_name,
                    document_type=doc.document_type,
                    document_file=doc.file,
                    description=doc.description,
                    source_application=application,
                )

            application.status = "approved"
            application.reviewed_by = request.user
            application.reviewed_on = timezone.now()
            application.vendor = vendor
            application.save()

            tender = application.tender
            tender.status = "awarded"
            tender.actual_amount = tender.projected_amount
            tender.save()

            if TenderAward.objects.filter(tender=tender, status="active").exists():
                return Response(
                    {"error": "This tender already has an active award."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            TenderAward.objects.create(
                tender=tender,
                vendor=vendor,
                award_amount=tender.projected_amount,
                status="active",
            )
            return Response(
                {
                    "message": "Tender application approved successfully.",
                    "vendor": VendorListSerializer(vendor).data,
                },
                status=status.HTTP_200_OK,
            )


class ReopenTenderView(APIView):
    def patch(self, request, *args, **kwargs):
        tender_id = kwargs.get("pk")

        try:
            tender = Tender.objects.get(pk=tender_id)
        except Tender.DoesNotExist:
            return Response(
                {"error": "Tender not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if tender.status not in ["awarded", "closed", "cancelled"]:
            return Response(
                {"error": "Only awarded or closed tenders can be reopened."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # revoke the existing award
        award = TenderAward.objects.filter(tender=tender, status="active").first()
        if award:
            award.status = "revoked"
            award.save()

        # Reopen the tender
        tender.status = "open"
        tender.save()

        return Response(
            {"message": "Tender has been reopened and is now open for applications."},
            status=status.HTTP_200_OK,
        )


class VendorListView(generics.ListAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VendorFilter

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            qs = self.filter_queryset(qs)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_qs = paginator.paginate_queryset(qs, request)
                serializer = self.get_serializer(paginated_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


class VendorDetailView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorListSerializer
    lookup_field = "pk"


class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PurchaseOrderCreateSerializer
        return PurchaseOrderListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, order_no=generate_order_no())


class GoodsReceivedCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        purchase_order_id = request.data.get("purchase_order")
        remarks = request.data.get("remarks", "")

        try:
            purchase_order = PurchaseOrder.objects.get(pk=purchase_order_id)
        except PurchaseOrder.DoesNotExist:
            return Response(
                {"error": "Purchase order not found."}, status=status.HTTP_404_NOT_FOUND
            )

        purchase_order.status = "received"
        purchase_order.save()

        goods_received = GoodsReceived.objects.create(
            purchase_order=purchase_order,
            received_by=self.request.user,
            remarks=remarks,
        )

        for item in purchase_order.items.all():
            PurchaseItemReceipt.objects.create(
                purchase_item=item,
                goods_received=goods_received,
                quantity_received=item.quantity,
            )

        return Response(
            {
                "message": "Goods received successfully.",
                "goods_received_id": goods_received.id,
                "purchase_order_status": purchase_order.status,
            },
            status=status.HTTP_201_CREATED,
        )


class VendorPaymentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VendorPaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        print(f"Award ID: {serializer.validated_data["tender_award"].id}")

        tender_award = serializer.validated_data["tender_award"]
        amount = serializer.validated_data["amount"]
        payment_method = serializer.validated_data["payment_method"]
        description = serializer.validated_data.get("description", "")
        print("tender_award_id", tender_award)

        # tender_award = get_object_or_404(TenderAward, id=tender_award_id)
        reference = generate_payment_reference()

        service = VendorPaymentService(
            tender_award=tender_award,
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            user=self.request.user,
            description=description,
        )

        try:
            payment = service.process_payment()
            return Response(
                {
                    "message": "Vendor payment processed successfully.",
                    "payment_id": payment.id,
                    "reference": payment.reference,
                    "amount": str(payment.amount),
                    "paid_by": self.request.user.username,
                    "payment_method": payment.payment_method,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VendorPaymentsAPIView(generics.ListAPIView):
    queryset = VendorPayment.objects.all().order_by("-created_on")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorPaymentListSerializer

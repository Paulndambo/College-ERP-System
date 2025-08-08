from rest_framework import serializers

from apps.users.serializers import UserSerializer
from .models import ApplicationDocument, Tender, TenderApplication, TenderAward, Vendor, PurchaseOrder, PurchaseItem, GoodsReceived, VendorPayment


class VendorPaymentCreateSerializer(serializers.ModelSerializer):
    # tender_award = serializers.PrimaryKeyRelatedField(queryset=TenderAward.objects.all())
    #tender_award = serializers.IntegerField()
    class Meta:
        model = VendorPayment
        fields = ["tender_award", "amount", "payment_method", "description"]
        extra_kwargs = {
            "description": {"required": False},
            "reference": {"required": True},
            "paid_by": {"required": True},
        }
class MinimalTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = "__all__"
class TenderAwardNestedSerializer(serializers.ModelSerializer):
    tender = MinimalTenderSerializer()

    class Meta:
        model = TenderAward
        fields = ["id", "tender", "status", "award_amount", "created_on","amount_paid"]
class MinimalVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["id", "name", "email", "phone", "address", "tax_pin", "company_registration_number"]
class VendorListSerializer(serializers.ModelSerializer):
    awards = TenderAwardNestedSerializer(many=True, read_only=True, source="awarded_tenders")
    class Meta:
        model = Vendor
        fields = "__all__"
class TenderAwardSerializer(serializers.ModelSerializer):
    vendor = VendorListSerializer(read_only=True)
    tender = MinimalTenderSerializer()
    class Meta:
        model = TenderAward
        fields = [
            "id",
            "status",
            "award_amount",
            "vendor",
            "created_on",
            "updated_on",
            "tender",
            "amount_paid",
            "balance_due",
            "payment_status"
        ]
class TenderListSerializer(serializers.ModelSerializer):
    award = TenderAwardSerializer(read_only=True)
    class Meta:
        model = Tender
        fields = [
            "id",
            "title",
            "description",
            "deadline",
            "status",
            "projected_amount",
            "actual_amount",
            "tender_document",
            "start_date",
            "end_date",
            "created_on",
            "updated_on",
            "award",
        ]


class TenderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = [
            "title",
            "description",
            "deadline",
            "start_date",
            "end_date",
            "tender_document",
            "status",
            "projected_amount",
            "actual_amount",
        ]
class TenderApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderApplication
        fields = [
            "tender",
            "company_name",
            "email",
            "phone",
            "address",
            "contact_person",
            "contact_person_phone",
            "contact_person_email",
            "business_type",
            "company_registration_number",
            "tax_pin",
            "vendor_no",
        ]
        extra_kwargs = {
            "vendor_no": {"required": False},
           
        }
    def validate(self, attrs):
        tender = attrs.get("tender")
        company_name = attrs.get("company_name")

        if TenderApplication.objects.filter(tender=tender, company_name__iexact=company_name).exists():
            raise serializers.ValidationError("This company has already applied for this tender.")

        return attrs
        

class TenderApplicationDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = ['application', 'document_name', 'document_type', 'file', 'description']

class TenderApplicationDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = "__all__"
class TenderApplicationListSerializer(serializers.ModelSerializer):
    tender =  TenderListSerializer(read_only=True)
    vendor = VendorListSerializer(read_only=True)
    documents = TenderApplicationDocumentListSerializer(many=True, read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    class Meta:
        model = TenderApplication
        fields = [
            "id",
            "tender",
            "status",
            "created_on",
            "updated_on",
            "reviewed_on",
            "reviewed_by",
            "phone",
            "email",
            "tax_pin",
            "company_registration_number",
            "business_type",
            "company_name",
            "contact_person",
            "contact_person_phone",
            "contact_person_email",
            "address",
            "vendor",
            "documents",
        ]


        

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['name', 'description', 'quantity', 'unit', 'unit_price', 'category']

class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, write_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'vendor', 'status', 'created_by', 'order_no', 'items']
        extra_kwargs = {
            'created_by': {'required': False},
            'status': {'required': False},
            'order_no': {'required': False},
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseItem.objects.create(purchase_order=purchase_order, **item_data)
        return purchase_order
class PurchaseOrderListSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)
    vendor = MinimalVendorSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    #  total_amount = serializers.SerializerMethodField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'vendor', 'status', 'created_on', 'items','total_amount', 'order_no', 'created_by']
    # def get_total_amount(self, obj):
    #     return sum([item.quantity * item.unit_price for item in obj.items.all()])

class GoodsReceivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceived
        fields = "__all__"


class VendorPaymentListSerializer(serializers.ModelSerializer):
    vendor = MinimalVendorSerializer(read_only=True)
    tender_award = TenderAwardNestedSerializer(read_only=True)
    paid_by = UserSerializer(read_only=True)
    class Meta:
        model = VendorPayment
        fields = "__all__"

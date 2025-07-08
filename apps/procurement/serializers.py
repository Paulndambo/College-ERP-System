from rest_framework import serializers
from .models import Vendor, PurchaseOrder, PurchaseItem, GoodsReceived, VendorPayment


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['id', 'description', 'quantity', 'unit_price']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'vendor', 'status', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        po = PurchaseOrder.objects.create(**validated_data)
        for item in items_data:
            PurchaseItem.objects.create(purchase_order=po, **item)
        return po


class GoodsReceivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceived
        fields = '__all__'


class VendorPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPayment
        fields = '__all__'

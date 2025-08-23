from rest_framework import serializers

from apps.inventory.models import Category, InventoryItem, StockIssue, UnitOfMeasure
from apps.schools.serializers import DepartmentListSerializer
from apps.users.serializers import UserSerializer

CATEGORY_TYPE_LABELS = {
    "fixed_asset": "Fixed Asset",
    "inventory": "Inventory",
    "consumable": "Consumable",
    "service": "Service",
    "other": "Other",
}


class UnitOfMeasureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = "__all__"


class CategoryListSerializer(serializers.ModelSerializer):
    category_type_label = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category_type_label"] = CATEGORY_TYPE_LABELS.get(
            instance.category_type, ""
        )
        return data


class InventoryItemListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer()
    unit = UnitOfMeasureListSerializer()

    class Meta:
        model = InventoryItem
        fields = "__all__"


class CreateInventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            "name",
            "description",
            "category",
            "quantity_in_stock",
            "unit",
            "unit_valuation",
            "total_valuation",
        ]
        extra_kwargs = {
            "description": {"required": False},
            "unit_valuation": {"required": False},
            "total_valuation": {"required": False},
        }


class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "category_type", "description"]
        extra_kwargs = {
            "description": {"required": False},
        }


class CreateUnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = ["name"]


class StockIssueSerializer(serializers.ModelSerializer):
    inventory_item_name = serializers.CharField(source='inventory_item.name', read_only=True)
    unit = serializers.CharField(source='inventory_item.unit.name', read_only=True)

    class Meta:
        model = StockIssue
        fields = [
            'id',
            'inventory_item',
            'inventory_item_name',
            'unit',
            'quantity',
            'issued_to',
            'issued_by',
            'remarks',
            'issued_on',
        ]
        read_only_fields = ['id', 'issued_by', 'issued_on', 'inventory_item_name', 'unit']

   
class StockIssueListSerializer(serializers.ModelSerializer):
    inventory_item = InventoryItemListSerializer()
    issued_by = UserSerializer(read_only=True)
    issued_to = DepartmentListSerializer(read_only=True)
    class Meta:
        model = StockIssue
        fields = [
            'id',
            'inventory_item',
            'quantity',
            'issued_to',
            'issued_by',
            'remarks',
            'issued_on',
        ]
        read_only_fields = ['id', 'issued_by', 'issued_on',]
from rest_framework import serializers

from apps.inventory.models import Category, InventoryItem, UnitOfMeasure
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
        data["category_type_label"] = CATEGORY_TYPE_LABELS.get(instance.category_type, "")
        return data
        
class InventoryItemListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer()
    unit = UnitOfMeasureListSerializer()
    class Meta:
        model = InventoryItem
        fields = "__all__"
        

        

    
class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name","category_type", "description"]
        extra_kwargs = {
            'description': {'required': False},
        }
        
class CreateUnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = ["name"]
        
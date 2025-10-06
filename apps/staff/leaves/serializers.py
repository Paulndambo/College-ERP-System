from rest_framework import serializers

from apps.staff.models import LeavePolicy


class LeavePolicyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePolicy
        fields = [
            "id",
            "name",
            "description",
            "default_days",
            "requires_document_after",
            "is_active",
        ]


class CreateAndUpdateLeavePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePolicy
        fields = [
            "name",
            "description",
            "default_days",
            "requires_document_after",
            "is_active",
        ]
        extra_kwargs = {
            "requires_document_after": {"required": False},
        }

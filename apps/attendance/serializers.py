from rest_framework import serializers

class StaffCheckInSerializer(serializers.Serializer):
    staff_number = serializers.CharField(
        source="staff.staff_number",
        read_only=True,
    )

    def validate(self, attrs):
        if attrs.get("check_out_time") and attrs["check_out_time"] < attrs["check_in_time"]:
            raise serializers.ValidationError("Check out time cannot be before check in time.")
        return attrs

    def create(self, validated_data):
        return super().create(validated_data)
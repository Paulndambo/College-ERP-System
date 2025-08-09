from rest_framework import serializers
from apps.staff.models import Payslip


class PayWagesCreateSerializer(serializers.Serializer):
    payslip = serializers.PrimaryKeyRelatedField(queryset=Payslip.objects.all())
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.ChoiceField(
        choices=[
            ("Cash", "Cash"),
            ("Bank", "Bank Transfer"),
            ("Mpesa", "Mpesa"),
            ("Cheque", "Cheque"),
        ]
    )
    notes = serializers.CharField(required=False, allow_blank=True)

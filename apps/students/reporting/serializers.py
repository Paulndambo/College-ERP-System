from rest_framework import serializers
from apps.students.models import SemesterReporting

class SemesterReportingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterReporting
        fields = "__all__"
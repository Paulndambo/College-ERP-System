from rest_framework import serializers

from apps.core.models import StudyYear
from apps.core.serializers import StudyYearListSerializer
from apps.schools.models import Programme, Semester
from apps.schools.serializers import ProgrammeListSerializer, SemesterListSerializer
from .models import FeeStructure, FeeStructureItem


class FeeStructureItemCreateUpdateSerializer(serializers.ModelSerializer):
    fee_structure = serializers.PrimaryKeyRelatedField(
        queryset=FeeStructure.objects.all()
    )

    class Meta:
        model = FeeStructureItem
        fields = ["id", "fee_structure", "description", "amount"]


class FeeStructureItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructureItem
        fields = ["id", "description", "amount"]


class FeeStructureCreateUpdateSerializer(serializers.ModelSerializer):
    programme = serializers.PrimaryKeyRelatedField(queryset=Programme.objects.all())
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())
    year_of_study = serializers.PrimaryKeyRelatedField(queryset=StudyYear.objects.all())

    class Meta:
        model = FeeStructure
        fields = ["id", "programme", "year_of_study", "semester"]


class FeeStructureListSerializer(serializers.ModelSerializer):
    programme = ProgrammeListSerializer()
    semester = SemesterListSerializer()
    year_of_study = StudyYearListSerializer()

    total = serializers.SerializerMethodField()

    class Meta:
        model = FeeStructure
        fields = ["id", "programme", "year_of_study", "semester", "total"]

    def get_total(self, obj):
        return obj.total_amount()

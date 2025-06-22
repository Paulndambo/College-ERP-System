from rest_framework import serializers
from .models import Campus, StudyYear, UserRole


class CampusCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = ["name", "city", "address", "phone_number", "email", "population"]


class CampusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = [
            "id",
            "name",
            "city",
            "address",
            "phone_number",
            "email",
            "population",
        ]


class StudyYearCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyYear
        fields = ["name"]


class StudyYearListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyYear
        fields = "__all__"


class UserRoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ["id", "name"]

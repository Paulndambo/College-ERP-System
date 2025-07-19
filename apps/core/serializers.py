from rest_framework import serializers

from apps.users.serializers import UserSerializer
from .models import Campus, StudyYear, UserRole
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType


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


class LogEntrySerializer(serializers.ModelSerializer):
    action_flag_display = serializers.SerializerMethodField()
    content_type = serializers.SlugRelatedField(read_only=True, slug_field="model")
    user = UserSerializer(read_only=True)

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "user",
            "action_time",
            "content_type",
            "object_repr",
            "action_flag",
            "action_flag_display",
            "change_message",
        ]

    def get_action_flag_display(self, obj):
        return obj.get_action_flag_display()

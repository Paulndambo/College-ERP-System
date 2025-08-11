from rest_framework import serializers

from apps.users.serializers import UserSerializer
from .models import Campus, RolePermission, StudyYear, UserRole,Module
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

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "name", "code"]

class RolePermissionSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)

    class Meta:
        model = RolePermission
        fields = [
            "id",
            "module",
            "can_view",
            "can_create",
            "can_edit",
            "can_delete",
            "can_approve",
            "can_export",
            "can_print"
        ]


class UserRoleListSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = UserRole
        fields = ["id", "name", "permissions"]

    def get_permissions(self, obj):
        role_permissions = RolePermission.objects.filter(role=obj)
        return RolePermissionSerializer(role_permissions, many=True).data

class RoleSerializer(serializers.ModelSerializer):
    modules = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserRole
        fields = ["id", "name", "modules", "permissions"]

    def get_permissions(self, obj):
        return [
            {
                "module": perm.module.id,
                "module_name": perm.module.name,
                "can_view": perm.can_view,
                "can_add": perm.can_create,
                "can_edit": perm.can_edit,
                "can_delete": perm.can_delete,
            }
            for perm in obj.rolepermission_set.all()
        ]

    def create(self, validated_data):
        modules_data = validated_data.pop("modules", [])
        role = UserRole.objects.create(**validated_data)
        for module_id in modules_data:
            module = Module.objects.get(id=module_id)
            RolePermission.objects.create(
                role=role,
                module=module,
                can_view=True,  # default true
                can_create=False,
                can_edit=False,
                can_delete=False,
            )
        return role

    def update(self, instance, validated_data):
        modules_data = validated_data.pop("modules", [])
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        
        instance.rolepermission_set.all().delete()  # clear old perms
        for module_id in modules_data:
            module = Module.objects.get(id=module_id)
            RolePermission.objects.create(
                role=instance,
                module=module,
                can_view=True,
                can_create=False,
                can_edit=False,
                can_delete=False,
            )
        return instance
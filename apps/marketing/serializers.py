from apps.schools.serializers import ProgrammeListSerializer
from rest_framework import serializers
from .models import Lead, Interaction, Campaign, Task, LeadStage


class InteractionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ["lead", "interaction_type", "notes", "date", "added_by"]


class InteractionListDetailSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source="lead.name", read_only=True)
    added_by_name = serializers.CharField(
        source="added_by.get_full_name", read_only=True
    )

    class Meta:
        model = Interaction
        fields = [
            "id",
            "lead",
            "lead_name",
            "interaction_type",
            "notes",
            "date",
            "added_by",
            "added_by_name",
            "created_on",
            "updated_on",
        ]


class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "name",
            "image",
            "campaign_type",
            "start_date",
            "end_date",
            "description",
            "status",
            "campaign_link",
            "budget",
        ]
        read_only_fields = ["slug", "views"]


class CampaignListDetailSerializer(serializers.ModelSerializer):
    lead_count = serializers.SerializerMethodField()
    conversion_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id",
            "name",
            "image",
            "campaign_type",
            "start_date",
            "end_date",
            "description",
            "status",
            "views",
            "slug",
            "campaign_link",
            "budget",
            "lead_count",
            "conversion_rate",
            "created_on",
            "updated_on",
        ]

    def get_lead_count(self, obj):
        return obj.leads.count()


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["user", "lead", "title", "description", "due_date", "completed"]


class TaskListDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    lead_name = serializers.CharField(source="lead.name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "user",
            "user_name",
            "lead",
            "lead_name",
            "title",
            "description",
            "due_date",
            "completed",
            "created_on",
            "updated_on",
        ]


class LeadStageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStage
        fields = ["lead", "stage", "date_reached", "added_by"]


class LeadStageListDetailSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source="lead.name", read_only=True)
    added_by_name = serializers.CharField(
        source="added_by.get_full_name", read_only=True
    )

    class Meta:
        model = LeadStage
        fields = [
            "id",
            "lead",
            "lead_name",
            "stage",
            "date_reached",
            "added_by",
            "added_by_name",
            "created_on",
            "updated_on",
        ]


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "gender",
            "source",
            "programme",
            "city",
            "country",
            "status",
            "score",
            "assigned_to",
            "campaign",
        ]


class LeadListDetailSerializer(serializers.ModelSerializer):
    programme = ProgrammeListSerializer(read_only=True)
    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name", read_only=True
    )
    campaign = CampaignListDetailSerializer(read_only=True) 

    class Meta:
        model = Lead
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "gender",
            "source",
            "programme",
            "city",
            "country",
            "status",
            "score",
            "assigned_to",
            "assigned_to_name",
            "campaign",
            "created_on",
            "updated_on",
        ]


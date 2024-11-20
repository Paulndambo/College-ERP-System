from django.utils import timezone
from django.db import models
from django.utils.text import slugify
from django.conf import settings

from apps.core.models import AbsoluteBaseModel

# 1. Lead model to store basic lead information
LEAD_STATUS_CHOICES = [
    ("New", "New"),
    ("Contacted", "Contacted"),
    ("Interested", "Interested"),
    ("Application in Progress", "Application in Progress"),
    ("Converted", "Converted"),
    ("Lost", "Lost"),
]

GENDER_CHOICES = (("Male", "Male"), ("Female", "Female"))

INTERACTION_TYPE_CHOICES = [
    ("Email", "Email"),
    ("Phone", "Phone"),
    ("SMS", "SMS"),
    ("Meeting", "Meeting"),
    ("Event", "Event"),
]

CAMPAIGN_TYPE_CHOICES = [
    ("Email", "Email Campaign"),
    ("Social Media", "Social Media Campaign"),
    ("Webinar", "Webinar"),
    ("Event", "Event"),
    ("Phone Call", "Phone Call"),
]

CAMPAIGN_STATUSES = (
    ("Draft", "Draft"),
    ("In Progress", "In Progress"),
    ("Completed", "Completed"),
)


class Lead(AbsoluteBaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    source = models.CharField(max_length=100)
    programme = models.ForeignKey("schools.Programme", on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=LEAD_STATUS_CHOICES, default="New")
    score = models.IntegerField(default=0, help_text="Lead scoring to prioritize leads")
    assigned_to = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="agentleads")
    campaign = models.ForeignKey("marketing.Campaign", on_delete=models.SET_NULL, null=True, related_name="leads")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def name(self):
        return f"{self.first_name} {self.last_name}"
# 2. Interaction model to track communication history with leads
class Interaction(AbsoluteBaseModel):
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name="interactions"
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    notes = models.TextField(help_text="Details of the interaction")
    date = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.interaction_type} with {self.lead.name} on {self.date.strftime('%Y-%m-%d')}"


# 3. Campaign model to manage marketing campaigns
class Campaign(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="campaigns_images/", null=True, blank=True)
    campaign_type = models.CharField(max_length=50, choices=CAMPAIGN_TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
    status = models.CharField(max_length=50, choices=CAMPAIGN_STATUSES, default="Draft")
    views = models.IntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True)
    campaign_link = models.URLField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.campaign_type})"

    def conversion_rate(self):
        converted = self.leads.filter(status="Converted").count()
        pending = self.leads.exclude(status="Converted").count()
        total_leads = self.leads.count()

        if converted == 0:
            return 0

        return (converted / total_leads) * 100


# 4. Task model to manage follow-up tasks
class Task(AbsoluteBaseModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="agenttasks"
    )
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Task for {self.lead.name}: {self.title} - {'Completed' if self.completed else 'Pending'}"


# 5. LeadStage model to track the stages of a lead's journey
class LeadStage(AbsoluteBaseModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="stages")
    stage = models.CharField(max_length=50, choices=LEAD_STATUS_CHOICES)
    date_reached = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.lead.name} reached {self.stage} on {self.date_reached.strftime('%Y-%m-%d')}"

from django.urls import path

from apps.marketing.views import (
    LeadsListView,
    lead_details,
    capture_lead,
    edit_lead,
    new_lead_interaction,
    add_lead_task,
    add_lead_stage,
    mark_task_as_complete,
    delete_lead_task,
    TasksListView,
    create_application_with_lead
)

from apps.marketing.campaigns.views import (
    campaigns,
    new_campaign,
    campaign_details,
    edit_campaign,
    campaign_drive,
    delete_campaign,
    interest_received,
    express_interest,
    CollectCampainsView,
)

from apps.marketing.uploads.views import upload_leads

urlpatterns = [
    path("leads/", LeadsListView.as_view(), name="leads"),
    path("leads/<int:lead_id>/details", lead_details, name="lead-details"),
    path("capture-lead/", capture_lead, name="capture-lead"),
    path("edit-lead/", edit_lead, name="edit-lead"),
    path("upload-leads/", upload_leads, name="upload-leads"),
    path("add-lead-interaction/", new_lead_interaction, name="add-lead-interaction"),
    path("tasks/", TasksListView.as_view(), name="tasks"),
    path("add-lead-task/", add_lead_task, name="add-lead-task"),
    path("add-lead-stage/", add_lead_stage, name="add-lead-stage"),
    path("mark-task-as-complete/", mark_task_as_complete, name="mark-task-as-complete"),
    path("delete-lead-task/", delete_lead_task, name="delete-lead-task"),
    path("start-application-with-lead/", create_application_with_lead, name="start-application-with-lead"),
    path("campaigns/", campaigns, name="campaigns"),
    path("campaigns/<int:campaign_id>/details", campaign_details, name="campaign-details"),
    path("new-campaign/", new_campaign, name="new-campaign"),
    path("edit-campaign/", edit_campaign, name="edit-campaign"),
    path("delete-campaign/", delete_campaign, name="delete-campaign"),
    path("campaign-drive/<slug:slug>/", campaign_drive, name="campaign-drive"),
    path("interest-received/", interest_received, name="interest-received"),
    path("express-interest/", express_interest, name="express-interest"),
    path(
        "collect-campaign-views/",
        CollectCampainsView.as_view(),
        name="collect-campaign-views",
    ),
]

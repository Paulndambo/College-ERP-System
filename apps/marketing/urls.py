from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    # Lead URLs
    path("leads/", views.LeadListView.as_view(), name="lead-list"),
    path("leads/<int:pk>/", views.LeadDetailView.as_view(), name="lead-detail"),
    path("leads/create/", views.LeadCreateView.as_view(), name="lead-create"),
    path("leads/<int:pk>/update/", views.LeadUpdateView.as_view(), name="lead-update"),
    # Interaction URLs
    path("interactions/", views.InteractionListView.as_view(), name="interaction-list"),
    path(
        "interactions/<int:pk>/",
        views.InteractionDetailView.as_view(),
        name="interaction-detail",
    ),
    path(
        "interactions/create/",
        views.InteractionCreateView.as_view(),
        name="interaction-create",
    ),
    path(
        "interactions/<int:pk>/update/",
        views.InteractionUpdateView.as_view(),
        name="interaction-update",
    ),
    # Campaign URLs
    path("campaigns/", views.CampaignListView.as_view(), name="campaign-list"),
    path(
        "campaigns/<slug:slug>/",
        views.CampaignDetailView.as_view(),
        name="campaign-detail",
    ),
    path(
        "campaigns/create/", views.CampaignCreateView.as_view(), name="campaign-create"
    ),
    path(
        "campaigns/<int:pk>/update/",
        views.CampaignUpdateView.as_view(),
        name="campaign-update",
    ),
    # Task URLs
    path("tasks/", views.TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/update/", views.TaskUpdateView.as_view(), name="task-update"),
    # LeadStage URLs
    path("lead-stages/", views.LeadStageListView.as_view(), name="lead-stage-list"),
    path(
        "lead-stages/<int:pk>/",
        views.LeadStageDetailView.as_view(),
        name="lead-stage-detail",
    ),
    path(
        "lead-stages/create/",
        views.LeadStageCreateView.as_view(),
        name="lead-stage-create",
    ),
    path(
        "lead-stages/<int:pk>/update/",
        views.LeadStageUpdateView.as_view(),
        name="lead-stage-update",
    ),
]

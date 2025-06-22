from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [
    path("marks-records/", views.ExamDataListAPIView.as_view(), name="marks-list"),
    path(
        "marks-records/create/",
        views.ExamDataCreateAPIView.as_view(),
        name="marks-create",
    ),
    path(
        "marks-records/upload/",
        views.BulkExamDataUploadAPIView.as_view(),
        name="marks-upload",
    ),
    path(
        "marks-records/<int:pk>/update/",
        views.ExamDatapdateAPIView.as_view(),
        name="marks-update",
    ),
    path("transcripts/", views.TranscriptsDataView.as_view(), name="transcript-list"),
]

from django.urls import path

from apps.exams.views import ExamMarksListView, record_marks, edit_marks, delete_marks

from apps.exams.uploads.views import upload_students_marks
from apps.exams.transcripts.views import (
    transcripts,
    semester_transcripts,
    semester_transcripts_details,
    department_transcripts,
    StudentsTranscriptsListView,
    student_transcripts_details,
)

urlpatterns = [
    path("students-marks/", ExamMarksListView.as_view(), name="students-marks"),
    path("record-marks/", record_marks, name="record-marks"),
    path("edit-marks/", edit_marks, name="edit-marks"),
    path("delete-marks/", delete_marks, name="delete-marks"),
    path("upload-marks/", upload_students_marks, name="upload-marks"),
    path("transcripts/", transcripts, name="transcripts"),
    path("semester-transcripts/", semester_transcripts, name="semester-transcripts"),
    path(
        "semester-transcripts/<int:semester_id>/",
        semester_transcripts_details,
        name="semester-transcripts-details",
    ),
    path(
        "department-transcripts/", department_transcripts, name="department-transcripts"
    ),
    path("student-transcripts/", StudentsTranscriptsListView.as_view(), name="student-transcripts"),
    path(
        "student-transcripts/<int:student_id>/",
        student_transcripts_details,
        name="student-transcripts-details",
    ),
]

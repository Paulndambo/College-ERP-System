from django.urls import path

from apps.students.reporting.views import (
    GraduateSingleStudentView,
    GraduateStudentsView,
    PromoteSingleStudentView,
    PromoteStudentsView,
    PromotionsListAPIView,
    ReportSemesterStudentsView,
    ReportSingleSemesterStudentView,
    SemesterReportingListAPIView,
)


from .views import (
    AssessmentList,
    StudentAccountUpdateView,
    StudentDetailView,
    StudentDocumentCreateView,
    StudentDocumentHistoryListView,
    StudentDocumentUpdateView,
    StudentEducationHistoryCreateView,
    StudentEducationHistoryListView,
    StudentEducationHistoryUpdateView,
    StudentListView,
    StudentMealCardCreateView,
    StudentMealCardListView,
    StudentMealCardUpdateView,
    StudentMetricsView,
    StudentProgrameCreateView,
    StudentProgrameListView,
    StudentProgrammeUpdateView,
    StudentRegistrationView,
    StudentUpdateView,
    BulkStudentUploadView,
)


urlpatterns = [
    # Students
    path("create-student/", StudentRegistrationView.as_view(), name="create-student"),
    path(
        "update-student/<int:pk>/", StudentUpdateView.as_view(), name="update-student"
    ),
    path("semester-reporting/bulk/", ReportSemesterStudentsView.as_view()),
    path("semester-reporting/single/", ReportSingleSemesterStudentView.as_view()),
    path("semester-reporting/", SemesterReportingListAPIView.as_view()),
    path("semester-reporting/promotions/", PromotionsListAPIView.as_view()),
    path("semester-reporting/promote-bulk/", PromoteStudentsView.as_view()),
    path(
        "semester-reporting/graduate-bulk/",
        GraduateStudentsView.as_view(),
        name="graduate-students",
    ),
    path(
        "semester-reporting/graduate-single/",
        GraduateSingleStudentView.as_view(),
        name="graduate-single-student",
    ),
    path("semester-reporting/promote-single/", PromoteSingleStudentView.as_view(), name="promote-single-student"),
    path(
        "update-student-account/<int:pk>/",
        StudentAccountUpdateView.as_view(),
        name="update-student-account",
    ),
    path("list/", StudentListView.as_view(), name="students-list"),
    path("assessment-list/", AssessmentList.as_view(), name="assessment-list"),
    path("<int:pk>/", StudentDetailView.as_view(), name="students-details"),
    path("upload/", BulkStudentUploadView.as_view(), name="student-bulk-upload"),
    # Eduaction history
    path(
        "education-history/create/",
        StudentEducationHistoryCreateView.as_view(),
        name="student-education-create",
    ),
    path(
        "education-history/",
        StudentEducationHistoryListView.as_view(),
        name="student-education-history",
    ),
    path(
        "education/update/<int:pk>/",
        StudentEducationHistoryUpdateView.as_view(),
        name="student-education-update",
    ),
    # Documents
    path(
        "documents/create/",
        StudentDocumentCreateView.as_view(),
        name="student-document-create",
    ),
    path(
        "documents/", StudentDocumentHistoryListView.as_view(), name="student-documents"
    ),
    path(
        "documents/update/<int:pk>/",
        StudentDocumentUpdateView.as_view(),
        name="student-document-update",
    ),
    # Programmes
    path(
        "programme/create/",
        StudentProgrameCreateView.as_view(),
        name="student-programme-create",
    ),
    path("programmes/", StudentProgrameListView.as_view(), name="student-programmes"),
    path(
        "programme/update/<int:pk>/",
        StudentProgrammeUpdateView.as_view(),
        name="student-programme-update",
    ),
    # Meal Cards
    path(
        "mealcards/create/",
        StudentMealCardCreateView.as_view(),
        name="student-mealcard-create",
    ),
    path("mealcards/", StudentMealCardListView.as_view(), name="student-mealcards"),
    path(
        "mealcards/update/<int:pk>/",
        StudentMealCardUpdateView.as_view(),
        name="student-mealcard-update",
    ),
    path(
        "metrics/",
        StudentMetricsView.as_view(),
        name="student-metrics",
    ),
    # path(
    #     "semester-reporting/",
    #     SemesterReportingAPIView.as_view(),
    #     name="semester-reporting",
    # ),
]

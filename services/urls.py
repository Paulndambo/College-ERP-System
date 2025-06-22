from django.urls import path, include
from .schema import schema_view


urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("students/", include("apps.students.urls")),
    path("core/", include("apps.core.urls")),
    path("schools/", include("apps.schools.urls")),
    path("admissions/", include("apps.admissions.urls")),
    path("academics/", include("apps.exams.urls")),
    path("marketing/", include("apps.marketing.urls")),
    path("library/", include("apps.library.urls")),
    path("staff/", include("apps.staff.urls")),
    path("hostels/", include("apps.hostels.urls")),
    path("payroll/", include("apps.payroll.urls")),
    path("fees/", include("apps.student_finance.urls")),
    # api documentation urls
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

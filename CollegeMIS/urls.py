"""
URL configuration for CollegeMIS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from services.schema import schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("apis/", include("services.urls")),
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
    path("finance/", include("apps.finance.urls")),
    path("accounts/", include("apps.accounting.urls")),
    path("procurement/", include("apps.procurement.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

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

urlpatterns = [
    # path("admin/", admin.site.urls),
    # path("", include("apps.core.urls")),
    # path("users/", include("apps.users.urls")),
    # path("students/", include("apps.students.urls")),
    # path("staff/", include("apps.staff.urls")),
    # path("payments/", include("apps.payments.urls")),
    # path("hostels/", include("apps.hostels.urls")),
    # path("schools/", include("apps.schools.urls")),
    # path("exams/", include("apps.exams.urls")),
    # path("library/", include("apps.library.urls")),
    # path("admissions/", include("apps.admissions.urls")),
    # path("marketing/", include("apps.marketing.urls")),
    # path("finance/", include("apps.finance.urls")),
    # path("visitors/", include("apps.visitors.urls")),

    #V2 - APIS
    path("apis/", include("services.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

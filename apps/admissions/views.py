from datetime import datetime
from django.shortcuts import render, redirect
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction


from django.views.generic import ListView
from django.http import JsonResponse

from apps.admissions.models import StudentApplication, ApplicationDocument

# Create your views here.
class StudentApplicationsListView(ListView):
    model = StudentApplication
    template_name = 'admissions/applications.html'
    context_object_name = 'applications'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(id_number__icontains=search_query),
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context
    

def application_details(request, id):
    application = StudentApplication.objects.get(id=id)
    
    context = {
        "application": application
    }
    return render(request, "admissions/application_details.html", context)
from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from tenants.models import Tenant
import logging
import time
from django.db import connection

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to monitor request performance and database queries"""
    
    def process_request(self, request):
        request.start_time = time.time()
        request.db_queries_start = len(connection.queries)
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            db_queries = len(connection.queries) - getattr(request, 'db_queries_start', 0)
            
            # Log slow requests (> 1 second) or requests with many queries (> 20)
            if duration > 1.0 or db_queries > 20:
                logger.warning(
                    f"Slow request: {request.path} - Duration: {duration:.2f}s, "
                    f"DB Queries: {db_queries}, Method: {request.method}"
                )
            
            # Add performance headers for debugging
            response['X-Request-Duration'] = f"{duration:.3f}"
            response['X-DB-Queries'] = str(db_queries)
        
        return response


class TenantMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.get_host().split(":")[0]  # Extract domain or subdomain
        logger.debug(f"Processing request for domain: {domain}")
        try:
            request.tenant = Tenant.objects.get(domain=domain)
            logger.debug(f"Tenant found: {request.tenant}")
        except Tenant.DoesNotExist:
            logger.warning(f"No tenant found for domain: {domain}")
            request.tenant = None
        response = self.get_response(request)
        return response


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            # Redirect to login page
            return redirect(reverse("login"))
        return None

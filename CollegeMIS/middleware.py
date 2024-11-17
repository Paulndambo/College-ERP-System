from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from tenants.models import Tenant
import logging

logger = logging.getLogger(__name__)


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
            # Allow access to login, logout, and any URL defined in LOGIN_EXEMPT_URLS
            if not any(
                request.path.startswith(url)
                for url in getattr(settings, "LOGIN_EXEMPT_URLS", [])
            ):
                return redirect(f"{reverse('login')}?next={request.path}")

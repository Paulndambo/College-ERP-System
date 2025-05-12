
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, CustomAPIException):
        return Response(
            {"error": exc.detail}, 
            status=exc.status_code
        )

   
    elif isinstance(exc, ValidationError):
        if isinstance(exc.detail, dict):
            error_fields = [f"{field}" for field in exc.detail.keys()]
            error_message = f"Validation failed: {', '.join(error_fields)} are required."
        else:
            error_message = "Validation error occurred."

        return Response(
            {"error": error_message},  
            status=status.HTTP_400_BAD_REQUEST
        )
    return response

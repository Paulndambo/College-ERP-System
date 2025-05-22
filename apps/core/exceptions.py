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
           
            if any(isinstance(v, list) and len(v) > 0 and "required" in v[0].lower() for v in exc.detail.values()):
              
                error_fields = [f"{field}" for field in exc.detail.keys()]
                error_message = f"{', '.join(error_fields)} required."
            elif "non_field_errors" in exc.detail:
           
                error_message = exc.detail["non_field_errors"][0]
            else:
              
                first_key = next(iter(exc.detail))
                messages = exc.detail[first_key]
                if isinstance(messages, list):
                    error_message = messages[0]
                else:
                    error_message = str(messages)
        else:
      
            error_message = str(exc.detail)
            if isinstance(exc.detail, list) and len(exc.detail) > 0:
                error_message = exc.detail[0]
        
        return Response(
            {"error": error_message},  
            status=status.HTTP_400_BAD_REQUEST
        )
    

    if response is None:
        return Response(
            {"error": "An unexpected error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
    return response

# from rest_framework.views import exception_handler
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.exceptions import ValidationError
# from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException

# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)

#     if isinstance(exc, CustomAPIException):
#         return Response(
#             {"error": exc.detail},
#             status=exc.status_code
#         )

    
#     elif isinstance(exc, ValidationError):
#         if isinstance(exc.detail, dict):
#             # If it's a dict, check if 'non_field_errors' exists
#             if "non_field_errors" in exc.detail:
#                 # Grab the first error from non_field_errors
#                 error_message = exc.detail["non_field_errors"][0]
#             else:
#                 # Fallback: grab first error message from any field
#                 first_key = next(iter(exc.detail))
#                 messages = exc.detail[first_key]
#                 if isinstance(messages, list):
#                     error_message = messages[0]
#                 else:
#                     error_message = str(messages)
#         elif isinstance(exc.detail, list):
#             error_message = exc.detail[0]
#         else:
#             error_message = str(exc.detail)

#         return Response(
#             {"error": error_message},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     return response

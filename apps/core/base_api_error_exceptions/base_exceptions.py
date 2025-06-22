from rest_framework.exceptions import APIException


class CustomAPIException(APIException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

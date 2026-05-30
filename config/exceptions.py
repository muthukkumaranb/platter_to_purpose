from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.exceptions import AppException


def global_exception_handler(exc, context):
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    # Catch custom domain exceptions (inheriting from AppException)
    if isinstance(exc, AppException):
        custom_data = {"error": exc.code, "detail": exc.detail}
        return Response(custom_data, status=exc.status_code)

    # Format standard DRF exceptions to follow the same payload convention
    if response is not None:
        error_code = "error"
        if response.status_code == 400:
            error_code = "bad_request"
        elif response.status_code == 401:
            error_code = "not_authenticated"
        elif response.status_code == 403:
            error_code = "permission_denied"
        elif response.status_code == 404:
            error_code = "not_found"
        elif response.status_code == 405:
            error_code = "method_not_allowed"

        # Keep original DRF error details (e.g. field errors dict) under "detail"
        response.data = {"error": error_code, "detail": response.data}

    return response

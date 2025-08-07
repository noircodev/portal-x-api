from rest_framework.views import exception_handler
from rest_framework.response import Response


def event_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            "status": "error",
            "success": False,
            "message": response.data.get("detail", "An error occurred"),
            "data": None
        }, status=response.status_code)

    return Response({
        "status": "error",
        "success": False,
        "message": "An unexpected error occurred",
        "data": None
    }, status=500)

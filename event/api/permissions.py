from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnlyOrAuthenticated(BasePermission):
    """
    Allow read-only requests for anyone, but write requests only for authenticated users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

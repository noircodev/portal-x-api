from rest_framework.permissions import SAFE_METHODS, BasePermission
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from django.http import HttpResponseForbidden, JsonResponse, Http404
from django.shortcuts import redirect, render


class IsAdminUserOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


class StaffOnlySwaggerView(SpectacularSwaggerView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            # return Http404()
            return render(request, 'home/error_page/page_not_found.html', status=404)
        return super().dispatch(request, *args, **kwargs)


class ReadOnlyOrAuthenticated(BasePermission):
    """
    Allow read-only requests for anyone, but write requests only for authenticated users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

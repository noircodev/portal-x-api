
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from event.models import Event
from event.api.serializers import EventSerializer
# Custom Bearer authentication
from event.api.authentication import BearerTokenAuthentication


class CustomPagination(PageNumberPagination):
    page_size = 10  # Set number of events per page
    page_size_query_param = 'page_size'
    max_page_size = 50


class ActiveEventListView(ListAPIView):
    serializer_class = EventSerializer
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Event.objects.filter(start_date__gt=timezone.now().date())

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "success": True,
                "message": "Active events retrieved successfully",
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "success": True,
            "message": "Active events retrieved successfully",
            "data": serializer.data
        })


active_event_list_view = ActiveEventListView.as_view()

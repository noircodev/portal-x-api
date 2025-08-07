from event.forms import SubmitEventForm, SubmitEventLinkForm, EventSearchForm
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.views import APIView
import meilisearch
from django.conf import settings
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from event.models import Event, City, BetaSubscriber
from event.api.serializers import (
    EventSerializer,
    BetaSubscriberSerializer,
    SubmitEventSerializer,
    CitySerializer,
    SearchQuerySerializer,
    SuggestionQuerySerializer,
    SearchSuggestionResponseSerializer,
    IndexResponseSerializer,
    ErrorResponseSerializer,
    ApiResponseSerializer
)
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny)
from rest_framework import serializers


# Pagination
class CustomPagination(PageNumberPagination):
    """Custom pagination class for API responses."""
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 100


# --- Active Events ---
@extend_schema_view(
    get=extend_schema(
        summary="List Active Events",
        description="Retrieve a paginated list of all active events (events with start date >= today)",
        responses={
            200: EventSerializer(many=True),
            400: ErrorResponseSerializer,
        },
        tags=["Events"]
    )
)
class ActiveEventListView(ListAPIView):
    """List all active events with pagination."""
    serializer_class = EventSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Event.objects.filter(
            start_date__gte=timezone.now().date(),
            valid=True
        ).select_related('city__region__country')


# --- Home Page (Index) ---
@extend_schema_view(
    get=extend_schema(
        summary="Home Page Events",
        description="Get events and featured events for the home page",
        responses={
            200: IndexResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["Events"]
    )
)
class IndexAPIView(ListAPIView):
    """Home page API endpoint returning events and featured events."""
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        """Get home page events and featured events."""
        try:
            events = Event.objects.filter(
                start_date__gte=timezone.now().date(),
                valid=True
            ).select_related('city__region__country')[:240]

            featured_events = Event.objects.filter(
                featured=True,
                start_date__gte=timezone.now().date(),
                valid=True
            ).select_related('city__region__country')[:5]

            return Response({
                "status": "success",
                "success": True,
                "message": "Events retrieved successfully",
                "events": EventSerializer(events, many=True).data,
                "featured_events": EventSerializer(featured_events, many=True).data
            })
        except Exception as e:
            return Response({
                "status": "error",
                "success": False,
                "message": "Failed to retrieve events",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    get=extend_schema(
        summary="List Active Cities",
        description="Get all active cities for event submission form",
        responses={
            200: CitySerializer(many=True),
            500: ErrorResponseSerializer,
        },
        tags=['Events']
    ),
    post=extend_schema(
        summary="Submit New Event",
        description="Submit a new event with optional image upload and user account creation",
        request=SubmitEventSerializer,
        responses={
            201: EventSerializer,
            400: ErrorResponseSerializer,
        },
        tags=['Events']
    )
)
class SubmitEventAPIView(ListCreateAPIView):
    """
    GET: List active cities for event submission.
    POST: Submit a new event with optional image upload and account creation.
    """
    serializer_class = SubmitEventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return City.objects.filter(active=True).select_related('region__country')

    def list(self, request, *args, **kwargs):
        """Get list of active cities for event submission form."""
        cities = self.get_queryset()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new event submission."""
        submission_type = request.data.get('submission_type', 'event')

        if submission_type == 'link':
            form = SubmitEventLinkForm(request.data)
        else:
            form = SubmitEventForm(request.data, request.FILES)

        if form.is_valid():
            event = form.save()
            return Response(
                EventSerializer(event).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"detail": "Validation failed", "field_errors": form.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# --- Beta Subscriber ---
@extend_schema_view(
    post=extend_schema(
        summary="Join Beta Program",
        description="Subscribe to the beta program with contact information",
        request=BetaSubscriberSerializer,
        responses={
            201: BetaSubscriberSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Beta"]
    )
)
class BetaSubscriberAPIView(CreateAPIView):
    """Subscribe to beta program."""
    serializer_class = BetaSubscriberSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Create a new beta subscriber."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscriber = serializer.save()

        return Response({
            "status": "success",
            "message": "Thank you for joining our beta program",
            "subscriber": BetaSubscriberSerializer(subscriber).data
        }, status=status.HTTP_201_CREATED)


# --- Search ---
@extend_schema_view(
    get=extend_schema(
        summary="Search Events",
        description="Search for events using a query string with pagination",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Search query for events'
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Page number for pagination'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Number of results per page (max 100)'
            ),
        ],
        responses={
            200: EventSerializer(many=True),
            400: ErrorResponseSerializer,
        },
        tags=['Search']
    )
)
class SearchResultAPIView(ListAPIView):
    """Search events with query string and pagination."""
    serializer_class = EventSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Get filtered events based on search query."""
        q_serializer = SearchQuerySerializer(data=self.request.query_params)
        q_serializer.is_valid(raise_exception=True)
        query = q_serializer.validated_data['q']

        form = EventSearchForm(self.request, {'q': query})
        if form.is_valid():
            return form.filter_event.select_related('city__region__country')
        return Event.objects.none()


@extend_schema_view(
    get=extend_schema(
        summary="Search Suggestions",
        description="Get autocomplete suggestions for search queries from events, cities, and zip codes",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Query string for autocomplete suggestions (minimum 1 character)'
            ),
        ],
        responses={
            200: SearchSuggestionResponseSerializer(many=True),
            400: ErrorResponseSerializer,
        },
        tags=['Search']
    )
)
class SearchSuggestionAPIView(APIView):
    """Get search suggestions from Meilisearch indices."""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Get autocomplete suggestions for search query."""
        q_serializer = SuggestionQuerySerializer(data=request.query_params)
        q_serializer.is_valid(raise_exception=True)
        query = q_serializer.validated_data['q']

        try:
            client = meilisearch.Client(
                settings.MEILISEARCH_URL,
                settings.MEILISEARCH_MASTER_KEY
            )

            # Search across different indices
            events = client.index("events").search(query, {"limit": 10}).get("hits", [])
            cities = client.index("cities").search(query, {"limit": 10}).get("hits", [])
            zips = client.index("zip_codes").search(query, {"limit": 10}).get("hits", [])

            # Format results
            results = []
            results.extend([{"name": e["title"], "type": "Event"} for e in events])
            results.extend([{"name": c["city_name"], "type": "City"} for c in cities])
            results.extend([{"name": z["zip_code"], "type": "ZipCode"} for z in zips])

            # Remove duplicates while preserving order
            seen = set()
            unique_results = []
            for item in results:
                key = item["name"].lower()
                if key not in seen:
                    seen.add(key)
                    unique_results.append(item)

            return Response(unique_results[:20])  # Limit to top 20 suggestions

        except Exception as e:
            return Response({
                "detail": f"Search service unavailable: {str(e)}"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

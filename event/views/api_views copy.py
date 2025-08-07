
from event.forms import SubmitEventForm, SubmitEventLinkForm, EventSearchForm
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.views import APIView
import meilisearch
from django.conf import settings
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from event.models import Event, City, BetaSubscriber
from event.api.serializers import (EventSerializer,
                                   BetaSubscriberSerializer,
                                   SubmitEventSerializer, CitySerializer, SearchQuerySerializer, SuggestionQuerySerializer)
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny)
from rest_framework import serializers
# Pagination


class CustomPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- Active Events ---


@extend_schema(tags=["Events"])
class ActiveEventListView(ListAPIView):
    serializer_class = EventSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Event.objects.filter(start_date__gte=timezone.now().date())

# --- Home Page (Index) ---


@extend_schema(tags=["Events"])
class IndexAPIView(ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        events = Event.objects.filter(start_date__gte=timezone.now().date())[:240]
        featured_events = Event.objects.filter(featured=True, start_date__gte=timezone.now().date())[:5]

        return Response({
            "status": "success",
            "success": True,
            "message": "Events retrieved successfully",
            "events": EventSerializer(events, many=True).data,
            "featured_events": EventSerializer(featured_events, many=True).data

        })


@extend_schema(
    tags=['Events'],
    request=EventSerializer,
    responses={201: EventSerializer, 400: "Validation Error"}
)
class SubmitEventAPIView(ListCreateAPIView):
    """
    POST: Submit a new event (with optional image upload).
    """
    serializer_class = SubmitEventSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        cities = City.objects.filter(active=True)
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        submission_type = request.data.get('submission_type', 'event')
        form = SubmitEventLinkForm(request.data) if submission_type == 'link' else SubmitEventForm(request.data, request.FILES)

        if form.is_valid():
            event = form.save()
            return Response(EventSerializer(event).data, status=201)

        return Response(form.errors, status=400)


# --- Search ---


@extend_schema(tags=["Beta"])
class BetaSubscriberAPIView(CreateAPIView):
    serializer_class = BetaSubscriberSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Thank you for joining our beta program", "subscriber": serializer.data},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    parameters=[SearchQuerySerializer],
    responses=EventSerializer(many=True),
    tags=['Search']
)
class SearchResultAPIView(ListAPIView):
    serializer_class = EventSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        q_serializer = SearchQuerySerializer(data=self.request.query_params)
        q_serializer.is_valid(raise_exception=True)
        query = q_serializer.validated_data['q']

        form = EventSearchForm(self.request, {'q': query})
        if form.is_valid():
            return form.filter_event
        return Event.objects.none()


@extend_schema(
    parameters=[SuggestionQuerySerializer],
    responses={
        200: serializers.ListSerializer(
            child=serializers.DictField(
                child=serializers.CharField()
            )
        )
    },
    tags=['Search']
)
class SearchSuggestionAPIView(APIView):
    def get(self, request, *args, **kwargs):
        q_serializer = SuggestionQuerySerializer(data=request.query_params)
        q_serializer.is_valid(raise_exception=True)
        query = q_serializer.validated_data['q']

        client = meilisearch.Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_MASTER_KEY)
        events = client.index("events").search(query).get("hits", [])
        cities = client.index("cities").search(query).get("hits", [])
        zips = client.index("zip_codes").search(query).get("hits", [])

        results = [{"name": e["title"], "type": "Event"} for e in events]
        results += [{"name": c["city_name"], "type": "City"} for c in cities]
        results += [{"name": z["zip_code"], "type": "ZipCode"} for z in zips]

        seen, unique_results = set(), []
        for item in results:
            key = item["name"].lower()
            if key not in seen:
                seen.add(key)
                unique_results.append(item)

        return Response(unique_results)


@extend_schema(
    tags=['Beta'],
    request=BetaSubscriberSerializer,
    responses={201: BetaSubscriberSerializer, 400: "Validation Error"}
)
class JoinBetaAPIView(CreateAPIView):
    queryset = BetaSubscriber.objects.all()
    serializer_class = BetaSubscriberSerializer

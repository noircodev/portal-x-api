from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from event.models import Country, Location, City
from event.api.serializers import CountrySerializer, LocationSerializer, CitySerializer
from event.api.permissions import ReadOnlyOrAuthenticated


# Country Views
@extend_schema_view(
    get=extend_schema(
        summary="List Countries",
        description="Retrieve a list of all countries with their ISO codes",
        responses={
            200: CountrySerializer(many=True),
            500: {'description': 'Internal server error'}
        },
        tags=['Geography']
    )
)
class CountryListView(ListAPIView):
    """List all countries."""
    queryset = Country.objects.filter(valided=True).order_by('country_name')
    serializer_class = CountrySerializer
    permission_classes = [ReadOnlyOrAuthenticated]


@extend_schema_view(
    get=extend_schema(
        summary="Get Country Details",
        description="Retrieve detailed information about a specific country",
        responses={
            200: CountrySerializer,
            404: {'description': 'Country not found'}
        },
        tags=['Geography']
    )
)
class CountryDetailView(RetrieveAPIView):
    """Retrieve a specific country by ID."""
    queryset = Country.objects.filter(valided=True)
    serializer_class = CountrySerializer
    permission_classes = [ReadOnlyOrAuthenticated]


@extend_schema_view(
    post=extend_schema(
        summary="Create Country",
        description="Create a new country entry (requires authentication)",
        request=CountrySerializer,
        responses={
            201: CountrySerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'}
        },
        tags=['Geography']
    )
)
class CountryCreateView(CreateAPIView):
    """Create a new country."""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [ReadOnlyOrAuthenticated]

    def perform_create(self, serializer):
        """Set default validation status."""
        serializer.save(valided=True)


@extend_schema_view(
    put=extend_schema(
        summary="Update Country",
        description="Update a country's information (requires authentication)",
        request=CountrySerializer,
        responses={
            200: CountrySerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'Country not found'}
        },
        tags=['Geography']
    ),
    patch=extend_schema(
        summary="Partial Update Country",
        description="Partially update a country's information (requires authentication)",
        request=CountrySerializer,
        responses={
            200: CountrySerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'Country not found'}
        },
        tags=['Geography']
    )
)
class CountryUpdateView(UpdateAPIView):
    """Update a country (full or partial)."""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [ReadOnlyOrAuthenticated]


@extend_schema_view(
    delete=extend_schema(
        summary="Delete Country",
        description="Delete a country (requires authentication)",
        responses={
            204: {'description': 'Country deleted successfully'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'Country not found'}
        },
        tags=['Geography']
    )
)
class CountryDeleteView(DestroyAPIView):
    """Delete a country."""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [ReadOnlyOrAuthenticated]


# Location (State) Views
@extend_schema_view(
    get=extend_schema(
        summary="List States/Locations",
        description="Retrieve a list of all states/locations with their countries",
        parameters=[
            OpenApiParameter(
                name='country',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by country ID'
            ),
            OpenApiParameter(
                name='active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status (default: true)'
            ),
        ],
        responses={
            200: LocationSerializer(many=True),
            400: {'description': 'Invalid query parameters'},
            500: {'description': 'Internal server error'}
        },
        tags=['Geography']
    )
)
class LocationListView(ListAPIView):
    """List all states/locations with optional filtering."""
    serializer_class = LocationSerializer
    permission_classes = [ReadOnlyOrAuthenticated]

    def get_queryset(self):
        """Get filtered queryset based on query parameters."""
        queryset = Location.objects.select_related("country").order_by('state_name', 'state_code')

        # Filter by country
        country_id = self.request.query_params.get('country')
        if country_id:
            queryset = queryset.filter(country_id=country_id)

        # Filter by active status (default: true)
        active = self.request.query_params.get('active', 'true').lower()
        if active in ['true', '1']:
            queryset = queryset.filter(active=True)
        elif active in ['false', '0']:
            queryset = queryset.filter(active=False)

        return queryset


@extend_schema_view(
    get=extend_schema(
        summary="Get State/Location Details",
        description="Retrieve detailed information about a specific state/location",
        responses={
            200: LocationSerializer,
            404: {'description': 'State/location not found'}
        },
        tags=['Geography']
    )
)
class LocationDetailView(RetrieveAPIView):
    """Retrieve a specific state/location by ID."""
    queryset = Location.objects.select_related("country")
    serializer_class = LocationSerializer
    permission_classes = [ReadOnlyOrAuthenticated]


@extend_schema_view(
    post=extend_schema(
        summary="Create State/Location",
        description="Create a new state/location entry (requires authentication)",
        request=LocationSerializer,
        responses={
            201: LocationSerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'}
        },
        tags=['Geography']
    )
)
class LocationCreateView(CreateAPIView):
    """Create a new state/location."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [ReadOnlyOrAuthenticated]

    def perform_create(self, serializer):
        """Set default active status."""
        serializer.save(active=True)


@extend_schema_view(
    put=extend_schema(
        summary="Update State/Location",
        description="Update a state/location's information (requires authentication)",
        request=LocationSerializer,
        responses={
            200: LocationSerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'State/location not found'}
        },
        tags=['Geography']
    ),
    patch=extend_schema(
        summary="Partial Update State/Location",
        description="Partially update a state/location's information (requires authentication)",
        request=LocationSerializer,
        responses={
            200: LocationSerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'State/location not found'}
        },
        tags=['Geography']
    )
)
class LocationUpdateView(UpdateAPIView):
    """Update a state/location (full or partial)."""
    queryset = Location.objects.select_related("country")
    serializer_class = LocationSerializer
    permission_classes = [ReadOnlyOrAuthenticated]


@extend_schema_view(
    delete=extend_schema(
        summary="Delete State/Location",
        description="Delete a state/location (requires authentication)",
        responses={
            204: {'description': 'State/location deleted successfully'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'State/location not found'}
        },
        tags=['Geography']
    )
)
class LocationDeleteView(DestroyAPIView):
    """Delete a state/location."""
    queryset = Location.objects.select_related("country")
    serializer_class = LocationSerializer
    permission_classes = [ReadOnlyOrAuthenticated]


# City Views
@extend_schema_view(
    get=extend_schema(
        summary="List Cities",
        description="Retrieve a list of all cities with their states and countries",
        parameters=[
            OpenApiParameter(
                name='region',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by region/state ID'
            ),
            OpenApiParameter(
                name='country',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by country ID'
            ),
            OpenApiParameter(
                name='active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status (default: true)'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search cities by name (case-insensitive)'
            ),
        ],
        responses={
            200: CitySerializer(many=True),
            400: {'description': 'Invalid query parameters'},
            500: {'description': 'Internal server error'}
        },
        tags=['Geography']
    )
)
class CityListView(ListAPIView):
    """List all cities with optional filtering and search."""
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAuthenticated]

    def get_queryset(self):
        """Get filtered queryset based on query parameters."""
        queryset = City.objects.select_related(
            "region",
            "region__country"
        ).order_by('region__state_name', 'city_ascii')

        # Filter by region/state
        region_id = self.request.query_params.get('region')
        if region_id:
            queryset = queryset.filter(region_id=region_id)

        # Filter by country
        country_id = self.request.query_params.get('country')
        if country_id:
            queryset = queryset.filter(region__country_id=country_id)

        # Filter by active status (default: true)
        active = self.request.query_params.get('active', 'true').lower()
        if active in ['true', '1']:
            queryset = queryset.filter(active=True)
        elif active in ['false', '0']:
            queryset = queryset.filter(active=False)

        # Search by city name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                city_name__icontains=search
            ) | queryset.filter(
                city_ascii__icontains=search
            )

        return queryset


@extend_schema_view(
    get=extend_schema(
        summary="Get City Details",
        description="Retrieve detailed information about a specific city",
        responses={
            200: CitySerializer,
            404: {'description': 'City not found'}
        },
        tags=['Geography']
    )
)
class CityDetailView(RetrieveAPIView):
    """Retrieve a specific city by ID."""
    queryset = City.objects.select_related("region", "region__country")
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAuthenticated]


@extend_schema_view(
    post=extend_schema(
        summary="Create City",
        description="Create a new city entry (requires authentication)",
        request=CitySerializer,
        responses={
            201: CitySerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'}
        },
        tags=['Geography']
    )
)
class CityCreateView(CreateAPIView):
    """Create a new city."""
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAuthenticated]

    def perform_create(self, serializer):
        """Set default active status to False for new cities."""
        serializer.save(active=False)


@extend_schema_view(
    put=extend_schema(
        summary="Update City",
        description="Update a city's information (requires authentication)",
        request=CitySerializer,
        responses={
            200: CitySerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'City not found'}
        },
        tags=['Geography']
    ),
    patch=extend_schema(
        summary="Partial Update City",
        description="Partially update a city's information (requires authentication)",
        request=CitySerializer,
        responses={
            200: CitySerializer,
            400: {'description': 'Validation errors'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'City not found'}
        },
        tags=['Geography']
    )
)
class CityUpdateView(UpdateAPIView):
    """Update a city (full or partial)."""
    queryset = City.objects.select_related("region", "region__country")
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAuthenticated]


@extend_schema_view(
    delete=extend_schema(
        summary="Delete City",
        description="Delete a city (requires authentication)",
        responses={
            204: {'description': 'City deleted successfully'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied'},
            404: {'description': 'City not found'}
        },
        tags=['Geography']
    )
)
class CityDeleteView(DestroyAPIView):
    """Delete a city."""
    queryset = City.objects.select_related("region", "region__country")
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAuthenticated]


# Alternative: Combined APIView approach (if you prefer single classes)
class CountryAPIView(APIView):
    """
    Combined API view for Country operations.
    Handles GET (list/detail), POST, PUT, PATCH, DELETE operations.
    """
    permission_classes = [ReadOnlyOrAuthenticated]

    @extend_schema(
        summary="List Countries or Get Country Details",
        description="List all countries or get specific country details",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=False,
                description='Country ID for detail view'
            ),
        ],
        responses={
            200: CountrySerializer(many=True),
            404: {'description': 'Country not found'}
        },
        tags=['Geography']
    )
    def get(self, request, pk=None):
        """Get all countries or specific country."""
        if pk:
            # Detail view
            country = get_object_or_404(Country, pk=pk, valided=True)
            serializer = CountrySerializer(country)
            return Response(serializer.data)
        else:
            # List view
            countries = Country.objects.filter(valided=True).order_by('country_name')
            serializer = CountrySerializer(countries, many=True)
            return Response(serializer.data)

    @extend_schema(
        summary="Create Country",
        description="Create a new country",
        request=CountrySerializer,
        responses={
            201: CountrySerializer,
            400: {'description': 'Validation errors'}
        },
        tags=['Geography']
    )
    def post(self, request):
        """Create a new country."""
        serializer = CountrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(valided=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update Country",
        description="Update a country",
        request=CountrySerializer,
        responses={
            200: CountrySerializer,
            400: {'description': 'Validation errors'},
            404: {'description': 'Country not found'}
        },
        tags=['Geography']
    )
    def put(self, request, pk):
        """Update a country (full update)."""
        country = get_object_or_404(Country, pk=pk)
        serializer = CountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partial Update Country",
        description="Partially update a country",
        request=CountrySerializer,
        responses={
            200: CountrySerializer,
            400: {'description': 'Validation errors'},
            404: {'description': 'Country not found'}
        },
        tags=['Geography']
    )
    def patch(self, request, pk):
        """Update a country (partial update)."""
        country = get_object_or_404(Country, pk=pk)
        serializer = CountrySerializer(country, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete Country",
        description="Delete a country",
        responses={
            204: {'description': 'Country deleted successfully'},
            404: {'description': 'Country not found'}
        },
        tags=['Geography']
    )
    def delete(self, request, pk):
        """Delete a country."""
        country = get_object_or_404(Country, pk=pk)
        country.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

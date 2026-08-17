from rest_framework import filters, generics

from airports.models import Airport
from airports.serializers import AirportSerializer
from avitrail.pagination import StandardResultsPagination
from avitrail.permissions import IsAdminOrReadOnly


class AirportListCreateView(generics.ListCreateAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["^ICAO", "^IATA", "name", "city"]

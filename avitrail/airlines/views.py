from rest_framework import filters, generics

from airlines.models import Airline
from airlines.serializers import AirlineSerializer
from avitrail.pagination import StandardResultsPagination
from avitrail.permissions import IsAdminOrReadOnly


class AirlineListCreateView(generics.ListCreateAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["^ICAO", "^IATA", "name"]

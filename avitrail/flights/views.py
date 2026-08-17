from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from avitrail.pagination import StandardResultsPagination
from flights.models import Flight
from flights.serializers import FlightSerializer


class FlightListCreateView(generics.ListCreateAPIView):
    serializer_class = FlightSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        return (
            Flight.objects.filter(user=self.request.user)
            .select_related("departure_airport", "arrival_airport", "airline")
            .order_by("-departure_time", "-id")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

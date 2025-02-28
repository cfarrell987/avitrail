from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from flights.models import Flight
from flights.serializers import FlightSerializer


# Create your views here.
class FlightListCreateView(generics.ListCreateAPIView):
    queryset = Flight.objects.all()
    filter_fields = ["airline", "departure", "arrival"]
    serializer_class = FlightSerializer
    permission_classes = [IsAuthenticated]

    def create(self, serializer):
        response = serializer.save(user=self.request.user)
        return response

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from airports.models import Airport
from airports.serializers import AirportSerializer


class AirportListCreateView(generics.ListCreateAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAuthenticated]

    def create(self, serializer):
        response = serializer.save(user=self.request.user)
        return response

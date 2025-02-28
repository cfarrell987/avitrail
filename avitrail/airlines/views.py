from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from airlines.models import Airline
from airlines.serializers import AirlineSerializer


class AirlineListCreateView(generics.ListCreateAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [IsAuthenticated]

    def create(self, serializer):
        response = serializer.save(user=self.request.user)
        return response

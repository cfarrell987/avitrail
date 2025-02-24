from rest_framework import serializers

from flights.models import Flight


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "__all__"

    def create(self, validated_data):
        flight = Flight.objects.create(**validated_data)
        return flight

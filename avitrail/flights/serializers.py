from datetime import datetime, timedelta, tzinfo

import pytz
from rest_framework import serializers

from airlines.serializers import AirlineSerializer
from airports.models import Airport
from airports.serializers import AirportSerializer
from flights.models import Flight


class FlightSerializer(serializers.ModelSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    airline = AirlineSerializer(read_only=True)

    # For write operations, accept IDs
    departure_airport_id = serializers.IntegerField(write_only=True)
    arrival_airport_id = serializers.IntegerField(write_only=True)
    airline_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "flight_number",
            "departure_time",
            "arrival_time",
            "duration",
            "aircraft",
            "distance",
            "tail_number",
            "departure_airport",
            "arrival_airport",
            "airline",
            "departure_airport_id",
            "arrival_airport_id",
            "airline_id",
        ]

    def calculate_duration(self, flight: Flight):
        # Calculate duration in minutes from the normalized times
        duration = flight.arrival_time - flight.departure_time
        return int(duration.total_seconds() // 60)

    def create(self, validated_data):
        # Remove nested data for creation
        departure_airport_id = validated_data.pop("departure_airport_id")
        arrival_airport_id = validated_data.pop("arrival_airport_id")
        airline_id = validated_data.pop("airline_id")

        departure_airport = Airport.objects.get(id=departure_airport_id)
        arrival_airport = Airport.objects.get(id=arrival_airport_id)

        # Update departure and arrival time to include timezone info from airport
        departure_time = validated_data["departure_time"]
        arrival_time = validated_data["arrival_time"]

        if departure_airport.timezone:
            departure_tz = pytz.timezone(departure_airport.timezone)
            validated_data["departure_time"] = departure_tz.localize(
                departure_time.replace(tzinfo=None)
            )
        if arrival_airport.timezone:
            arrival_tz = pytz.timezone(arrival_airport.timezone)
            validated_data["arrival_time"] = arrival_tz.localize(
                arrival_time.replace(tzinfo=None)
            )

        flight = Flight.objects.create(
            departure_airport_id=departure_airport_id,
            arrival_airport_id=arrival_airport_id,
            airline_id=airline_id,
            **validated_data
        )

        flight.duration = self.calculate_duration(flight)
        flight.save()
        return flight

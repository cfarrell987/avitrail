import pytz
from rest_framework import serializers

from airlines.models import Airline
from airlines.serializers import AirlineSerializer
from airports.models import Airport
from airports.serializers import AirportSerializer
from flights.models import Flight
from flights.utils import haversine_km


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
        read_only_fields = ["duration", "distance"]

    def validate(self, attrs):
        try:
            departure_airport = Airport.objects.get(id=attrs["departure_airport_id"])
        except Airport.DoesNotExist:
            raise serializers.ValidationError(
                {"departure_airport_id": "Airport not found."}
            )
        try:
            arrival_airport = Airport.objects.get(id=attrs["arrival_airport_id"])
        except Airport.DoesNotExist:
            raise serializers.ValidationError(
                {"arrival_airport_id": "Airport not found."}
            )
        try:
            airline = Airline.objects.get(id=attrs["airline_id"])
        except Airline.DoesNotExist:
            raise serializers.ValidationError({"airline_id": "Airline not found."})

        departure_time = attrs["departure_time"]
        arrival_time = attrs["arrival_time"]

        # Closed/defunct reference data stays selectable (for logging old
        # flights that predate the closure) but can't be used for anything
        # after the date it closed.
        if (
            departure_airport.disabled_at
            and departure_time > departure_airport.disabled_at
        ):
            raise serializers.ValidationError(
                {
                    "departure_airport_id": (
                        f"{departure_airport.name} was closed on "
                        f"{departure_airport.disabled_at:%Y-%m-%d} and can't be used "
                        f"for flights departing after that date."
                    )
                }
            )
        if arrival_airport.disabled_at and arrival_time > arrival_airport.disabled_at:
            raise serializers.ValidationError(
                {
                    "arrival_airport_id": (
                        f"{arrival_airport.name} was closed on "
                        f"{arrival_airport.disabled_at:%Y-%m-%d} and can't be used "
                        f"for flights arriving after that date."
                    )
                }
            )
        if airline.disabled_at and departure_time > airline.disabled_at:
            raise serializers.ValidationError(
                {
                    "airline_id": (
                        f"{airline.name} ceased operating on "
                        f"{airline.disabled_at:%Y-%m-%d} and can't be used for "
                        f"flights departing after that date."
                    )
                }
            )

        attrs["_departure_airport"] = departure_airport
        attrs["_arrival_airport"] = arrival_airport
        attrs["_airline"] = airline
        return attrs

    def create(self, validated_data):
        departure_airport_id = validated_data.pop("departure_airport_id")
        arrival_airport_id = validated_data.pop("arrival_airport_id")
        airline_id = validated_data.pop("airline_id")
        departure_airport = validated_data.pop("_departure_airport")
        arrival_airport = validated_data.pop("_arrival_airport")
        validated_data.pop("_airline")

        # Update departure and arrival time to include timezone info from airport
        departure_time = validated_data["departure_time"]
        arrival_time = validated_data["arrival_time"]

        if departure_airport.timezone:
            departure_tz = pytz.timezone(departure_airport.timezone)
            departure_time = departure_tz.localize(departure_time.replace(tzinfo=None))
            validated_data["departure_time"] = departure_time
        if arrival_airport.timezone:
            arrival_tz = pytz.timezone(arrival_airport.timezone)
            arrival_time = arrival_tz.localize(arrival_time.replace(tzinfo=None))
            validated_data["arrival_time"] = arrival_time

        # duration/distance are computed server-side — never trust client-submitted values
        duration = int((arrival_time - departure_time).total_seconds() // 60)

        distance = 0
        if None not in (
            departure_airport.lat,
            departure_airport.lon,
            arrival_airport.lat,
            arrival_airport.lon,
        ):
            distance = round(
                haversine_km(
                    departure_airport.lat,
                    departure_airport.lon,
                    arrival_airport.lat,
                    arrival_airport.lon,
                )
            )

        return Flight.objects.create(
            departure_airport_id=departure_airport_id,
            arrival_airport_id=arrival_airport_id,
            airline_id=airline_id,
            duration=duration,
            distance=distance,
            **validated_data,
        )

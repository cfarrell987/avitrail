from datetime import datetime, timezone as dt_timezone

from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airlines.models import Airline
from airports.models import Airport
from flights.admin import FlightAdmin
from flights.models import Flight


class FlightListCreateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="pilot", password="pass12345")
        self.other_user = User.objects.create_user(
            username="other", password="pass12345"
        )
        self.airline = Airline.objects.create(ICAO="UAL", IATA="UA", name="United")
        self.lax = Airport.objects.create(
            ICAO="KLAX", IATA="LAX", name="Los Angeles", lat=33.9425, lon=-118.408
        )
        self.jfk = Airport.objects.create(
            ICAO="KJFK", IATA="JFK", name="New York", lat=40.6413, lon=-73.7781
        )

    def test_list_only_returns_own_flights(self):
        Flight.objects.create(
            user=self.user,
            flight_number="UA1",
            departure_airport=self.lax,
            arrival_airport=self.jfk,
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
            duration=300,
            airline=self.airline,
            distance=1000,
        )
        Flight.objects.create(
            user=self.other_user,
            flight_number="UA2",
            departure_airport=self.lax,
            arrival_airport=self.jfk,
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
            duration=300,
            airline=self.airline,
            distance=1000,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/flights/flights/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["flight_number"], "UA1")

    def test_create_computes_duration_and_distance_server_side(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/flights/flights/",
            {
                "flight_number": "UA100",
                "departure_time": "2026-01-01T10:00:00Z",
                "arrival_time": "2026-01-01T15:00:00Z",
                "departure_airport_id": self.lax.id,
                "arrival_airport_id": self.jfk.id,
                "airline_id": self.airline.id,
                # client attempts to lie about duration/distance — must be ignored
                "duration": 1,
                "distance": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(flight_number="UA100")
        self.assertEqual(flight.user, self.user)
        self.assertEqual(flight.duration, 300)
        self.assertGreater(flight.distance, 3000)  # real LAX->JFK distance ~3980km

    def test_create_localizes_times_to_airport_timezones(self):
        self.lax.timezone = "America/Los_Angeles"
        self.lax.save()
        self.jfk.timezone = "America/New_York"
        self.jfk.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/flights/flights/",
            {
                "flight_number": "UA100",
                # Naive local times, as the datetime-local input sends them.
                "departure_time": "2026-01-01T10:00:00Z",
                "arrival_time": "2026-01-01T13:00:00Z",
                "departure_airport_id": self.lax.id,
                "arrival_airport_id": self.jfk.id,
                "airline_id": self.airline.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(flight_number="UA100")
        # 10:00 Pacific -> 18:00 UTC, 13:00 Eastern -> 18:00 UTC same day:
        # a 0-hour flight per the wall-clock times given, once localized.
        self.assertEqual(flight.departure_time.hour, 18)
        self.assertEqual(flight.arrival_time.hour, 18)

    def test_invalid_departure_airport_id_returns_400_not_500(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/flights/flights/",
            {
                "flight_number": "UA100",
                "departure_time": "2026-01-01T10:00:00Z",
                "arrival_time": "2026-01-01T15:00:00Z",
                "departure_airport_id": 999999,
                "arrival_airport_id": self.jfk.id,
                "airline_id": self.airline.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("departure_airport_id", response.data)

    def test_invalid_arrival_airport_id_returns_400_not_500(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/flights/flights/",
            {
                "flight_number": "UA100",
                "departure_time": "2026-01-01T10:00:00Z",
                "arrival_time": "2026-01-01T15:00:00Z",
                "departure_airport_id": self.lax.id,
                "arrival_airport_id": 999999,
                "airline_id": self.airline.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("arrival_airport_id", response.data)

    def test_invalid_airline_id_returns_400_not_500(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/flights/flights/",
            {
                "flight_number": "UA100",
                "departure_time": "2026-01-01T10:00:00Z",
                "arrival_time": "2026-01-01T15:00:00Z",
                "departure_airport_id": self.lax.id,
                "arrival_airport_id": self.jfk.id,
                "airline_id": 999999,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("airline_id", response.data)


class FlightAdminTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="pilot", password="pass12345")
        self.airline = Airline.objects.create(ICAO="UAL", IATA="UA", name="United")
        self.lax = Airport.objects.create(ICAO="KLAX", IATA="LAX", name="Los Angeles")
        self.jfk = Airport.objects.create(ICAO="KJFK", IATA="JFK", name="New York")
        self.flight = Flight.objects.create(
            user=self.user,
            flight_number="UA1",
            departure_airport=self.lax,
            arrival_airport=self.jfk,
            departure_time=datetime(2026, 1, 1, 10, 0, tzinfo=dt_timezone.utc),
            arrival_time=datetime(2026, 1, 1, 15, 0, tzinfo=dt_timezone.utc),
            duration=300,
            airline=self.airline,
            distance=1000,
        )

    def test_display_methods(self):
        self.assertEqual(
            FlightAdmin.departure_time(None, self.flight), "2026-01-01 10:00:00"
        )
        self.assertEqual(
            FlightAdmin.arrival_time(None, self.flight), "2026-01-01 15:00:00"
        )
        self.assertEqual(
            FlightAdmin.duration(None, self.flight),
            self.flight.arrival_time - self.flight.departure_time,
        )


class DisabledReferenceDataTests(APITestCase):
    """Airports/airlines are never deleted — closed/defunct ones are marked
    disabled_at instead, stay pickable for old flights, but block anything
    dated after the closure."""

    def setUp(self):
        self.user = User.objects.create_user(username="pilot", password="pass12345")
        self.client.force_authenticate(user=self.user)
        self.airline = Airline.objects.create(ICAO="UAL", IATA="UA", name="United")
        self.lax = Airport.objects.create(
            ICAO="KLAX", IATA="LAX", name="Los Angeles", lat=33.9425, lon=-118.408
        )
        self.jfk = Airport.objects.create(
            ICAO="KJFK", IATA="JFK", name="New York", lat=40.6413, lon=-73.7781
        )
        self.closed_at = datetime(2020, 1, 1, tzinfo=dt_timezone.utc)

    def _post_flight(self, departure_time, arrival_time, **overrides):
        payload = {
            "flight_number": "UA1",
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "departure_airport_id": self.lax.id,
            "arrival_airport_id": self.jfk.id,
            "airline_id": self.airline.id,
        }
        payload.update(overrides)
        return self.client.post("/api/flights/flights/", payload)

    def test_flight_after_airport_closure_rejected(self):
        self.lax.disabled_at = self.closed_at
        self.lax.save()

        response = self._post_flight("2026-01-01T10:00:00Z", "2026-01-01T15:00:00Z")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("departure_airport_id", response.data)

    def test_flight_after_arrival_airport_closure_rejected(self):
        self.jfk.disabled_at = self.closed_at
        self.jfk.save()

        response = self._post_flight("2026-01-01T10:00:00Z", "2026-01-01T15:00:00Z")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("arrival_airport_id", response.data)

    def test_flight_before_airport_closure_allowed(self):
        self.lax.disabled_at = self.closed_at
        self.lax.save()

        response = self._post_flight("2015-06-01T10:00:00Z", "2015-06-01T15:00:00Z")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_flight_after_airline_closure_rejected(self):
        self.airline.disabled_at = self.closed_at
        self.airline.save()

        response = self._post_flight("2026-01-01T10:00:00Z", "2026-01-01T15:00:00Z")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("airline_id", response.data)

    def test_disabled_airport_still_listed(self):
        self.lax.disabled_at = self.closed_at
        self.lax.save()

        response = self.client.get("/api/airports/airports/?search=Los")
        codes = [a["ICAO"] for a in response.data["results"]]
        self.assertIn("KLAX", codes)

    def test_protect_blocks_deleting_referenced_airport(self):
        Flight.objects.create(
            user=self.user,
            flight_number="UA1",
            departure_airport=self.lax,
            arrival_airport=self.jfk,
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
            duration=300,
            airline=self.airline,
            distance=1000,
        )
        with self.assertRaises(ProtectedError):
            self.lax.delete()

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airports.admin import AirportAdmin
from airports.models import Airport


class AirportCodeFormatTests(APITestCase):
    """ICAO location indicators are 4 uppercase letters (ICAO Doc 7910);
    IATA airport codes are 3 uppercase letters."""

    def test_valid_codes_pass(self):
        airport = Airport(ICAO="KLAX", IATA="LAX", name="Los Angeles Intl")
        airport.full_clean()

    def test_icao_wrong_length_rejected(self):
        airport = Airport(ICAO="LAX", IATA="LAX", name="Los Angeles Intl")
        with self.assertRaises(ValidationError):
            airport.full_clean()

    def test_icao_lowercase_rejected(self):
        airport = Airport(ICAO="klax", IATA="LAX", name="Los Angeles Intl")
        with self.assertRaises(ValidationError):
            airport.full_clean()

    def test_icao_with_digit_rejected(self):
        airport = Airport(ICAO="KLA1", IATA="LAX", name="Los Angeles Intl")
        with self.assertRaises(ValidationError):
            airport.full_clean()

    def test_iata_wrong_length_rejected(self):
        airport = Airport(ICAO="KLAX", IATA="LAXX", name="Los Angeles Intl")
        with self.assertRaises(ValidationError):
            airport.full_clean()

    def test_blank_iata_allowed(self):
        airport = Airport(ICAO="KLAX", IATA=None, name="Los Angeles Intl")
        airport.full_clean()


class AirportLifecycleTests(APITestCase):
    def test_is_active_reflects_disabled_at(self):
        airport = Airport.objects.create(ICAO="KLAX", IATA="LAX", name="LAX")
        self.assertTrue(airport.is_active)

        airport.disabled_at = timezone.now()
        airport.save()
        self.assertFalse(airport.is_active)

    def test_empty_string_iata_normalized_to_null_on_save(self):
        # bulk_create() (used by the import commands) bypasses save(), so
        # this normalization only kicks in on the ORM's normal save path —
        # covered separately by the import command's own tests.
        airport = Airport(ICAO="KLAX", IATA="", name="LAX")
        airport.save()
        self.assertIsNone(airport.IATA)


class AirportAdminTests(APITestCase):
    def test_timezone_display_method(self):
        airport = Airport(
            ICAO="KLAX", IATA="LAX", name="LAX", timezone="America/Los_Angeles"
        )
        self.assertEqual(AirportAdmin.timezone(None, airport), "America/Los_Angeles")


class AirportUniquenessTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "pass")
        self.client.force_authenticate(user=self.admin)

    def test_duplicate_iata_rejected_with_400_not_500(self):
        Airport.objects.create(ICAO="KLAX", IATA="LAX", name="Los Angeles Intl")
        response = self.client.post(
            "/api/airports/airports/",
            {"ICAO": "KBUR", "IATA": "LAX", "name": "Duplicate IATA"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_airports_without_iata_do_not_collide(self):
        Airport.objects.create(ICAO="KAAA", IATA=None, name="Airport A")
        response = self.client.post(
            "/api/airports/airports/", {"ICAO": "KBBB", "name": "Airport B"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AirportSearchTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("pilot", password="pass12345")
        self.client.force_authenticate(user=self.user)
        Airport.objects.create(
            ICAO="KLAX", IATA="LAX", name="Los Angeles Intl", city="Los Angeles"
        )
        Airport.objects.create(
            ICAO="KJFK", IATA="JFK", name="John F Kennedy Intl", city="New York"
        )

    def test_search_by_iata_prefix(self):
        response = self.client.get("/api/airports/airports/?search=LAX")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["ICAO"], "KLAX")

    def test_search_by_city_substring(self):
        response = self.client.get("/api/airports/airports/?search=York")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["ICAO"], "KJFK")

    def test_list_is_paginated(self):
        response = self.client.get("/api/airports/airports/")
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)

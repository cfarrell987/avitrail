from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airlines.models import Airline


class AirlineCodeFormatTests(APITestCase):
    """ICAO airline designators are 3 uppercase letters (ICAO Doc 8585);
    IATA airline codes are 2 characters, letters and/or digits."""

    def test_valid_codes_pass(self):
        airline = Airline(ICAO="UAL", IATA="UA", name="United Airlines")
        airline.full_clean()

    def test_valid_alphanumeric_iata_pass(self):
        # Real examples: Jet Airways "9W", IndiGo "6E".
        airline = Airline(ICAO="JAI", IATA="9W", name="Jet Airways")
        airline.full_clean()

    def test_icao_wrong_length_rejected(self):
        airline = Airline(ICAO="UA", IATA="UA", name="United Airlines")
        with self.assertRaises(ValidationError):
            airline.full_clean()

    def test_icao_with_digit_rejected(self):
        airline = Airline(ICAO="UA1", IATA="UA", name="United Airlines")
        with self.assertRaises(ValidationError):
            airline.full_clean()

    def test_iata_wrong_length_rejected(self):
        airline = Airline(ICAO="UAL", IATA="UAX", name="United Airlines")
        with self.assertRaises(ValidationError):
            airline.full_clean()

    def test_blank_codes_allowed(self):
        airline = Airline(ICAO=None, IATA=None, name="No Codes Airline")
        airline.full_clean()


class AirlineLifecycleTests(APITestCase):
    def test_is_active_reflects_disabled_at(self):
        airline = Airline.objects.create(ICAO="UAL", IATA="UA", name="United")
        self.assertTrue(airline.is_active)

        airline.disabled_at = timezone.now()
        airline.save()
        self.assertFalse(airline.is_active)

    def test_empty_string_codes_normalized_to_null_on_save(self):
        # bulk_create() (used by the import commands) bypasses save(), so
        # this normalization only kicks in on the ORM's normal save path —
        # covered separately by the import command's own tests.
        airline = Airline(ICAO="", IATA="", name="Blank Codes Airline")
        airline.save()
        self.assertIsNone(airline.ICAO)
        self.assertIsNone(airline.IATA)


class AirlineUniquenessTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "pass")
        self.client.force_authenticate(user=self.admin)

    def test_duplicate_icao_rejected_with_400_not_500(self):
        Airline.objects.create(ICAO="UAL", IATA="UA", name="United Airlines")
        response = self.client.post(
            "/api/airlines/airlines/",
            {"ICAO": "UAL", "IATA": "XX", "name": "Duplicate ICAO"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_airlines_without_codes_do_not_collide(self):
        Airline.objects.create(ICAO=None, IATA=None, name="Airline A")
        response = self.client.post("/api/airlines/airlines/", {"name": "Airline B"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AirlineSearchTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("pilot", password="pass12345")
        self.client.force_authenticate(user=self.user)
        Airline.objects.create(ICAO="UAL", IATA="UA", name="United Airlines")
        Airline.objects.create(ICAO="DAL", IATA="DL", name="Delta Air Lines")

    def test_search_by_name_substring(self):
        response = self.client.get("/api/airlines/airlines/?search=Delta")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["ICAO"], "DAL")

    def test_search_by_iata_prefix(self):
        response = self.client.get("/api/airlines/airlines/?search=UA")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["ICAO"], "UAL")

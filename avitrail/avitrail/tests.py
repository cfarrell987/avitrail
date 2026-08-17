import json
from io import StringIO
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser
from django.core.management import CommandError, call_command
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from airlines.models import Airline
from airports.models import Airport
from avitrail.management.commands.import_airlines import (
    Command as ImportAirlinesCommand,
)
from avitrail.management.commands.import_airports import (
    Command as ImportAirportsCommand,
)
from avitrail.permissions import IsAdminOrReadOnly


class IsAdminOrReadOnlyTests(TestCase):
    def setUp(self):
        self.permission = IsAdminOrReadOnly()
        self.factory = RequestFactory()

    def test_unauthenticated_request_denied(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))


class ImportAirportsSyncDisabledTests(TestCase):
    """Isolated tests for the disable/re-enable logic — no network calls,
    exercises the sync_disabled() helper directly with a fabricated source
    set instead of mocking requests.get()."""

    def setUp(self):
        self.command = ImportAirportsCommand()
        self.lax = Airport.objects.create(ICAO="KLAX", IATA="LAX", name="Los Angeles")
        self.jfk = Airport.objects.create(ICAO="KJFK", IATA="JFK", name="New York")

    def test_airport_missing_from_source_gets_disabled(self):
        disabled, reenabled = self.command.sync_disabled({"KJFK"})

        self.lax.refresh_from_db()
        self.jfk.refresh_from_db()
        self.assertEqual(disabled, 1)
        self.assertEqual(reenabled, 0)
        self.assertIsNotNone(self.lax.disabled_at)
        self.assertIsNone(self.jfk.disabled_at)

    def test_airport_back_in_source_gets_reenabled(self):
        self.lax.disabled_at = timezone.now()
        self.lax.save()

        disabled, reenabled = self.command.sync_disabled({"KLAX", "KJFK"})

        self.lax.refresh_from_db()
        self.assertEqual(disabled, 0)
        self.assertEqual(reenabled, 1)
        self.assertIsNone(self.lax.disabled_at)

    def test_already_disabled_airport_not_touched_again(self):
        self.lax.disabled_at = timezone.now()
        self.lax.save()
        original_disabled_at = self.lax.disabled_at

        disabled, reenabled = self.command.sync_disabled({"KJFK"})

        self.lax.refresh_from_db()
        self.assertEqual(disabled, 0)
        self.assertEqual(self.lax.disabled_at, original_disabled_at)


class ImportAirlinesSyncDisabledTests(TestCase):
    def setUp(self):
        self.command = ImportAirlinesCommand()
        self.ual = Airline.objects.create(ICAO="UAL", IATA="UA", name="United")
        self.dal = Airline.objects.create(ICAO="DAL", IATA="DL", name="Delta")
        self.no_code_airline = Airline.objects.create(name="Some Regional Carrier")

    def test_airline_gone_or_inactive_gets_disabled(self):
        # DAL absent from active_icaos == gone or flagged inactive upstream.
        disabled, reenabled = self.command.sync_disabled({"UAL"})

        self.ual.refresh_from_db()
        self.dal.refresh_from_db()
        self.assertEqual(disabled, 1)
        self.assertIsNone(self.ual.disabled_at)
        self.assertIsNotNone(self.dal.disabled_at)

    def test_airline_without_a_code_is_never_touched(self):
        # Can't be matched against active_icaos at all — must be left alone
        # rather than disabled on every single run.
        disabled, reenabled = self.command.sync_disabled({"UAL", "DAL"})

        self.no_code_airline.refresh_from_db()
        self.assertIsNone(self.no_code_airline.disabled_at)

    def test_airline_active_again_gets_reenabled(self):
        self.dal.disabled_at = timezone.now()
        self.dal.save()

        disabled, reenabled = self.command.sync_disabled({"UAL", "DAL"})

        self.dal.refresh_from_db()
        self.assertEqual(reenabled, 1)
        self.assertIsNone(self.dal.disabled_at)


def _mock_http_response(body):
    response = MagicMock()
    response.content = body.encode("utf-8")
    response.raise_for_status = MagicMock()
    return response


class ImportAirportsHandleTests(TestCase):
    """Exercises the full command (fetch -> filter -> validate -> bulk_create
    -> sync_disabled), not just the standalone sync_disabled() helper —
    with requests.get() mocked so no real network call is made."""

    CSV_BODY = (
        "icao_code,iata_code,name,municipality,iso_country,elevation_ft,"
        "latitude_deg,longitude_deg,scheduled_service\n"
        "KJFK,JFK,John F Kennedy Intl,New York,US,13,40.6413,-73.7781,yes\n"
        "KLAX,LAX,Los Angeles Intl,Los Angeles,US,125,33.9425,-118.408,yes\n"
        "K123,ABC,Has A Digit In ICAO,Nowhere,US,,0,0,yes\n"
        "KNOI,,No IATA Code,Nowhere,US,,0,0,yes\n"
        "K-AB,BAD,Fails Format Validation,Nowhere,US,,0,0,yes\n"
        "KGON,GON,Not Scheduled Service,Nowhere,US,,0,0,no\n"
    )

    def setUp(self):
        # Already present under this ICAO -> should be skipped, not duplicated.
        Airport.objects.create(ICAO="KLAX", IATA="LAX", name="Existing LAX")

    @patch("avitrail.management.commands.import_airports.requests.get")
    def test_handle_imports_new_and_skips_rest(self, mock_get):
        mock_get.return_value = _mock_http_response(self.CSV_BODY)

        call_command("import_airports", stdout=StringIO())

        self.assertTrue(Airport.objects.filter(ICAO="KJFK").exists())
        self.assertEqual(Airport.objects.filter(ICAO="KLAX").count(), 1)
        self.assertFalse(Airport.objects.filter(ICAO="K123").exists())
        self.assertFalse(Airport.objects.filter(ICAO="KNOI").exists())
        self.assertFalse(Airport.objects.filter(ICAO="K-AB").exists())
        self.assertFalse(Airport.objects.filter(ICAO="KGON").exists())

    @patch("avitrail.management.commands.import_airports.requests.get")
    def test_handle_disables_airport_missing_from_source(self, mock_get):
        Airport.objects.create(ICAO="KOLD", name="Old Closed Airport")
        mock_get.return_value = _mock_http_response(self.CSV_BODY)

        call_command("import_airports", stdout=StringIO())

        self.assertIsNotNone(Airport.objects.get(ICAO="KOLD").disabled_at)

    @patch("avitrail.management.commands.import_airports.requests.get")
    def test_handle_wipe_deletes_existing_first(self, mock_get):
        mock_get.return_value = _mock_http_response(self.CSV_BODY)

        call_command("import_airports", wipe=True, yes=True, stdout=StringIO())

        # KLAX from setUp() had a placeholder name — wipe+reimport replaces it
        # with the row from CSV_BODY, proving the old row was actually gone.
        self.assertEqual(Airport.objects.get(ICAO="KLAX").name, "Los Angeles Intl")

    @patch("builtins.input", return_value="no")
    def test_wipe_without_yes_prompts_and_aborts_on_decline(self, mock_input):
        with self.assertRaises(CommandError):
            call_command("import_airports", wipe=True, stdout=StringIO())
        mock_input.assert_called_once()
        # Nothing was touched — the prompt was declined before any deletion.
        self.assertTrue(Airport.objects.filter(ICAO="KLAX").exists())

    @patch("avitrail.management.commands.import_airports.requests.get")
    @patch("builtins.input")
    def test_wipe_on_empty_table_skips_confirmation(self, mock_input, mock_get):
        Airport.objects.all().delete()
        mock_get.return_value = _mock_http_response(self.CSV_BODY)

        call_command("import_airports", wipe=True, stdout=StringIO())

        mock_input.assert_not_called()

    @patch("avitrail.management.commands.import_airports.requests.get")
    def test_handle_reenables_airport_back_in_source(self, mock_get):
        self.jfk = Airport.objects.create(
            ICAO="KJFK", IATA="JFK", name="JFK", disabled_at=timezone.now()
        )
        mock_get.return_value = _mock_http_response(self.CSV_BODY)

        call_command("import_airports", stdout=StringIO())

        self.assertIsNone(Airport.objects.get(ICAO="KJFK").disabled_at)

    @patch("avitrail.management.commands.import_airports.requests.get")
    def test_handle_bad_coordinates_fall_back_to_utc(self, mock_get):
        # Blank (not garbage) lat/lon: float("") raises ValueError, hitting
        # the except branch, while still leaving lat/lon as None — a garbage
        # string like "not-a-number" would also fail the model's own
        # FloatField validation and get skipped before reaching this at all.
        body = self.CSV_BODY.replace(
            "KJFK,JFK,John F Kennedy Intl,New York,US,13,40.6413,-73.7781,yes",
            "KJFK,JFK,John F Kennedy Intl,New York,US,13,,,yes",
        )
        mock_get.return_value = _mock_http_response(body)

        call_command("import_airports", stdout=StringIO())

        self.assertEqual(Airport.objects.get(ICAO="KJFK").timezone, "UTC")

    @patch("avitrail.management.commands.import_airports.Airport.objects.bulk_create")
    @patch("avitrail.management.commands.import_airports.requests.get")
    def test_handle_bulk_create_integrity_error_raises_command_error(
        self, mock_get, mock_bulk_create
    ):
        mock_get.return_value = _mock_http_response(self.CSV_BODY)
        mock_bulk_create.side_effect = IntegrityError("duplicate key")

        with self.assertRaises(CommandError):
            call_command("import_airports", stdout=StringIO())


class ImportAirlinesHandleTests(TestCase):
    JSON_BODY = json.dumps(
        [
            {
                "icao": "UAL",
                "iata": "UA",
                "callsign": "UNITED",
                "name": "United Airlines",
                "country": "United States",
                "active": "Y",
            },
            {
                "icao": "DAL",
                "iata": "DL",
                "callsign": "DELTA",
                "name": "Delta Air Lines",
                "country": "United States",
                "active": "Y",
            },
            {
                "icao": "XXX",
                "iata": "XX",
                "callsign": "DEFUNCT",
                "name": "Defunct Airline",
                "country": "Nowhere",
                "active": "N",
            },
            {
                "icao": "BAD",
                "iata": "1",
                "callsign": "BADFMT",
                "name": "Bad IATA Format",
                "country": "Nowhere",
                "active": "Y",
            },
        ]
    )

    def setUp(self):
        # Already present -> should be skipped, not duplicated.
        Airline.objects.create(ICAO="DAL", IATA="DL", name="Existing Delta")

    @patch("avitrail.management.commands.import_airlines.requests.get")
    def test_handle_imports_new_and_skips_rest(self, mock_get):
        mock_get.return_value = _mock_http_response(self.JSON_BODY)

        call_command("import_airlines", stdout=StringIO())

        self.assertTrue(Airline.objects.filter(ICAO="UAL").exists())
        self.assertEqual(Airline.objects.filter(ICAO="DAL").count(), 1)
        self.assertFalse(Airline.objects.filter(ICAO="XXX").exists())  # inactive
        self.assertFalse(Airline.objects.filter(ICAO="BAD").exists())  # bad IATA

    @patch("avitrail.management.commands.import_airlines.requests.get")
    def test_handle_disables_airline_missing_or_inactive(self, mock_get):
        Airline.objects.create(ICAO="OLD", name="Old Defunct Carrier")
        mock_get.return_value = _mock_http_response(self.JSON_BODY)

        call_command("import_airlines", stdout=StringIO())

        self.assertIsNotNone(Airline.objects.get(ICAO="OLD").disabled_at)

    @patch("avitrail.management.commands.import_airlines.requests.get")
    def test_handle_wipe_deletes_existing_first(self, mock_get):
        mock_get.return_value = _mock_http_response(self.JSON_BODY)

        call_command("import_airlines", wipe=True, yes=True, stdout=StringIO())

        self.assertEqual(Airline.objects.get(ICAO="DAL").name, "Delta Air Lines")

    @patch("builtins.input", return_value="no")
    def test_wipe_without_yes_prompts_and_aborts_on_decline(self, mock_input):
        with self.assertRaises(CommandError):
            call_command("import_airlines", wipe=True, stdout=StringIO())
        mock_input.assert_called_once()
        self.assertTrue(Airline.objects.filter(ICAO="DAL").exists())

    @patch("avitrail.management.commands.import_airlines.requests.get")
    @patch("builtins.input")
    def test_wipe_on_empty_table_skips_confirmation(self, mock_input, mock_get):
        Airline.objects.all().delete()
        mock_get.return_value = _mock_http_response(self.JSON_BODY)

        call_command("import_airlines", wipe=True, stdout=StringIO())

        mock_input.assert_not_called()

    @patch("avitrail.management.commands.import_airlines.requests.get")
    def test_handle_reenables_airline_active_again(self, mock_get):
        Airline.objects.filter(ICAO="DAL").update(disabled_at=timezone.now())
        mock_get.return_value = _mock_http_response(self.JSON_BODY)

        call_command("import_airlines", stdout=StringIO())

        self.assertIsNone(Airline.objects.get(ICAO="DAL").disabled_at)

    @patch("avitrail.management.commands.import_airlines.Airline.objects.bulk_create")
    @patch("avitrail.management.commands.import_airlines.requests.get")
    def test_handle_bulk_create_integrity_error_raises_command_error(
        self, mock_get, mock_bulk_create
    ):
        mock_get.return_value = _mock_http_response(self.JSON_BODY)
        mock_bulk_create.side_effect = IntegrityError("duplicate key")

        with self.assertRaises(CommandError):
            call_command("import_airlines", stdout=StringIO())

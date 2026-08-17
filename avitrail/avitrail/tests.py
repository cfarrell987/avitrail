from django.test import TestCase
from django.utils import timezone

from airlines.models import Airline
from airports.models import Airport
from avitrail.management.commands.import_airlines import (
    Command as ImportAirlinesCommand,
)
from avitrail.management.commands.import_airports import (
    Command as ImportAirportsCommand,
)


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

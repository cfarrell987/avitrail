import csv

import requests
import timezonefinder
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.utils import timezone
from tqdm import tqdm

from airports.models import Airport

SOURCE_URL = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/refs/heads/main/airports.csv"


class Command(BaseCommand):
    help = (
        "Import new airports from the OurAirports dataset. Airports whose ICAO "
        "code already exists are skipped, so re-running only picks up additions. "
        "Airports no longer present in the source are marked disabled rather "
        "than deleted, since flights may still reference them."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Delete all existing airports first, forcing a full re-import.",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip the --wipe confirmation prompt (for scripting).",
        )

    def handle(self, *args, **options):
        if options["wipe"]:
            self._wipe(options["yes"])

        tf = timezonefinder.TimezoneFinder()

        self.stdout.write("Fetching OurAirports dataset...")
        resp = requests.get(SOURCE_URL)
        resp.raise_for_status()

        all_rows = list(csv.DictReader(resp.content.decode("utf-8").splitlines()))
        source_icaos = {
            row["icao_code"].strip().upper()
            for row in all_rows
            if row["icao_code"].strip()
        }
        rows = [row for row in all_rows if row["scheduled_service"] == "yes"]

        # Pre-fetch every code we already have in one query each, instead of
        # a per-row `.exists()` query — the old version issued one DB round
        # trip per CSV row (thousands of rows).
        seen_icaos = set(Airport.objects.values_list("ICAO", flat=True))
        seen_iatas = set(
            Airport.objects.exclude(IATA=None).values_list("IATA", flat=True)
        )

        new_airports = []
        skipped = 0
        invalid = 0

        for row in tqdm(rows, desc="Processing airports"):
            icao = row["icao_code"].strip().upper()
            iata = row["iata_code"].strip().upper()

            # A digit in the ICAO code excludes most small non-commercial
            # airports, which don't get real ICAO location indicators.
            if (
                not icao
                or icao in seen_icaos
                or any(char.isdigit() for char in icao)
                or not iata
                or iata in seen_iatas
            ):
                skipped += 1
                continue

            try:
                latitude = round(float(row["latitude_deg"]), 1)
                longitude = round(float(row["longitude_deg"]), 1)
                tz_str = tf.timezone_at(lat=latitude, lng=longitude) or "UTC"
            except (KeyError, ValueError):
                tz_str = "UTC"

            airport = Airport(
                ICAO=icao,
                IATA=iata,
                name=row["name"],
                city=row["municipality"] or None,
                country=row["iso_country"] or None,
                elevation=row["elevation_ft"] or None,
                lat=row["latitude_deg"] or None,
                lon=row["longitude_deg"] or None,
                timezone=tz_str,
            )

            try:
                # validate_unique=False: uniqueness against the DB is already
                # covered by the seen_icaos/seen_iatas check above, which also
                # catches collisions *within* this same import batch — a bare
                # full_clean() would miss those since bulk_create never hits
                # the DB until after this loop finishes.
                airport.full_clean(validate_unique=False)
            except ValidationError as e:
                invalid += 1
                self.stdout.write(
                    self.style.WARNING(f"Skipping {icao}: {e.message_dict}")
                )
                continue

            seen_icaos.add(icao)
            seen_iatas.add(iata)
            new_airports.append(airport)

        if new_airports:
            try:
                Airport.objects.bulk_create(new_airports)
            except IntegrityError as e:
                raise CommandError(f"Bulk insert failed, no airports were saved: {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(new_airports)} new airports "
                f"({skipped} already present/ineligible, {invalid} failed validation)."
            )
        )

        disabled, reenabled = self.sync_disabled(source_icaos)
        if disabled:
            self.stdout.write(
                self.style.WARNING(
                    f"Marked {disabled} airport(s) disabled (no longer in source)."
                )
            )
        if reenabled:
            self.stdout.write(
                self.style.SUCCESS(f"Re-enabled {reenabled} airport(s) back in source.")
            )

    def sync_disabled(self, source_icaos):
        """Mark airports missing from `source_icaos` as disabled, and clear
        disabled_at for any that have reappeared. Never deletes a row —
        flights may reference it. Returns (disabled_count, reenabled_count).
        """
        disabled = (
            Airport.objects.filter(disabled_at__isnull=True)
            .exclude(ICAO__in=source_icaos)
            .update(disabled_at=timezone.now())
        )
        reenabled = Airport.objects.filter(
            disabled_at__isnull=False, ICAO__in=source_icaos
        ).update(disabled_at=None)
        return disabled, reenabled

    def _wipe(self, confirmed):
        count = Airport.objects.count()
        if not count:
            return
        if not confirmed:
            answer = input(
                f"This will permanently delete all {count} existing airports. "
                f"Type 'yes' to continue: "
            )
            if answer.strip().lower() != "yes":
                raise CommandError("Aborted.")
        Airport.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"Deleted {count} airports."))

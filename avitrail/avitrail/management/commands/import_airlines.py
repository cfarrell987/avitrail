import json

import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.utils import timezone
from tqdm import tqdm

from airlines.models import Airline

SOURCE_URL = "https://raw.githubusercontent.com/npow/airline-codes/refs/heads/master/airlines.json"


class Command(BaseCommand):
    help = (
        "Import new airlines from the airline-codes dataset. Airlines whose ICAO "
        "code already exists are skipped, so re-running only picks up additions. "
        "Airlines no longer active in the source are marked disabled rather "
        "than deleted, since flights may still reference them."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Delete all existing airlines first, forcing a full re-import.",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip the --wipe confirmation prompt (for scripting).",
        )

    def handle(self, *args, **options):
        if options["wipe"]:
            self._wipe(options["yes"])

        self.stdout.write("Fetching airline-codes dataset...")
        resp = requests.get(SOURCE_URL)
        resp.raise_for_status()
        rows = json.loads(resp.content.decode("utf-8"))

        active_icaos = {
            row["icao"].strip().upper()
            for row in rows
            if row.get("active") == "Y" and (row.get("icao") or "").strip()
        }

        # Pre-fetch every code we already have in one query each, instead of
        # a per-row `.exists()` query — the old version issued one DB round
        # trip per JSON row (thousands of rows).
        seen_icaos = set(
            Airline.objects.exclude(ICAO=None).values_list("ICAO", flat=True)
        )
        seen_iatas = set(
            Airline.objects.exclude(IATA=None).values_list("IATA", flat=True)
        )

        new_airlines = []
        skipped = 0
        invalid = 0

        for row in tqdm(rows, desc="Processing airlines"):
            if row.get("active") != "Y":
                skipped += 1
                continue

            # bulk_create() never calls Model.save(), so the blank -> NULL
            # normalization on Airline.save() doesn't run here — many
            # regional carriers have no IATA code at all in this dataset,
            # and '' == '' would collide under the unique constraint the
            # very first time two of them landed in the same bulk_create().
            icao = (row.get("icao") or "").strip().upper() or None
            iata = (row.get("iata") or "").strip().upper() or None

            if (icao and icao in seen_icaos) or (iata and iata in seen_iatas):
                skipped += 1
                continue

            airline = Airline(
                ICAO=icao,
                IATA=iata,
                callsign=row.get("callsign") or None,
                name=row.get("name") or "",
                country=row.get("country") or None,
            )

            try:
                # validate_unique=False: uniqueness against the DB is already
                # covered by the seen_icaos/seen_iatas check above, which also
                # catches collisions *within* this same import batch — a bare
                # full_clean() would miss those since bulk_create never hits
                # the DB until after this loop finishes.
                airline.full_clean(validate_unique=False)
            except ValidationError as e:
                invalid += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {row.get('name', '?')}: {e.message_dict}"
                    )
                )
                continue

            if icao:
                seen_icaos.add(icao)
            if iata:
                seen_iatas.add(iata)
            new_airlines.append(airline)

        if new_airlines:
            try:
                Airline.objects.bulk_create(new_airlines)
            except IntegrityError as e:
                raise CommandError(f"Bulk insert failed, no airlines were saved: {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(new_airlines)} new airlines "
                f"({skipped} already present/inactive, {invalid} failed validation)."
            )
        )

        disabled, reenabled = self.sync_disabled(active_icaos)
        if disabled:
            self.stdout.write(
                self.style.WARNING(
                    f"Marked {disabled} airline(s) disabled (gone or inactive in source)."
                )
            )
        if reenabled:
            self.stdout.write(
                self.style.SUCCESS(f"Re-enabled {reenabled} airline(s) active again.")
            )

    def sync_disabled(self, active_icaos):
        """Mark airlines whose ICAO isn't in `active_icaos` as disabled, and
        clear disabled_at for any that are active again. Never deletes a
        row — flights may reference it. Returns (disabled_count, reenabled_count).
        """
        disabled = (
            Airline.objects.filter(disabled_at__isnull=True)
            .exclude(ICAO__in=active_icaos)
            .exclude(ICAO=None)
            .update(disabled_at=timezone.now())
        )
        reenabled = Airline.objects.filter(
            disabled_at__isnull=False, ICAO__in=active_icaos
        ).update(disabled_at=None)
        return disabled, reenabled

    def _wipe(self, confirmed):
        count = Airline.objects.count()
        if not count:
            return
        if not confirmed:
            answer = input(
                f"This will permanently delete all {count} existing airlines. "
                f"Type 'yes' to continue: "
            )
            if answer.strip().lower() != "yes":
                raise CommandError("Aborted.")
        Airline.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"Deleted {count} airlines."))

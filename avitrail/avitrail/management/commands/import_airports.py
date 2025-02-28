import os
import requests
import certifi
import ssl

from django.db import IntegrityError

from airports.models import Airport
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import airports from mwgg/Airports repository"

    def handle(self, *args, **kwargs):
        """
        Pull latest airports JSON from mwgg/Airports repository and save them to the airports table
        """

        import json
        from airports.models import Airport

        resp = requests.get(
            "https://raw.githubusercontent.com/mwgg/Airports/refs/heads/master/airports.json"
        )
        airports_data = json.loads(resp.content.decode("utf-8"))

        airports = []

        self.stdout.write(f"Importing airports from OurAirports")

        for airport in airports_data.values():
            airport = Airport(
                ICAO=airport["icao"],
                IATA=airport["iata"],
                name=airport["name"],
                city=airport["city"],
                country=airport["country"],
                elevation=airport["elevation"],
                lat=airport["lat"],
                lon=airport["lon"],
                timezone=airport["tz"],
            )
            airports.append(airport)

        if airports:
            self.stdout.write("Importing airports...")
            try:
                Airport.objects.bulk_create(airports)
            # Catch Integrity Error
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to save airport: {airport}. Error: {e}")
                )

        self.stdout.write(self.style.SUCCESS("Successfully imported airports"))

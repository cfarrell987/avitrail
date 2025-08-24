from django.db import IntegrityError

from airports.models import Airport
from django.core.management.base import BaseCommand

from airports.models import Airport


class Command(BaseCommand):
    help = "Import airports from mwgg/Airports repository"

    def handle(self, *args, **kwargs):
        """
        Pull latest airports JSON from mwgg/Airports repository and save them to the airports table
        """
        import json
        import requests
        import csv
        from tqdm import tqdm
        import timezonefinder

        tf = timezonefinder.TimezoneFinder()

        resp = requests.get(
            "https://raw.githubusercontent.com/davidmegginson/ourairports-data/refs/heads/main/airports.csv"
        )

        airports_data = [
            row
            for row in csv.DictReader(resp.content.decode("utf-8").splitlines())
            if row["scheduled_service"] == "yes"
        ]
        # Filter out airports with no scheduled_service
        airports_data = [
            airport
            for airport in airports_data
            if airport["scheduled_service"] == "yes"
        ]

        airports = []

        self.stdout.write(f"Importing airports from OurAirports")

        for airport in tqdm(airports_data, desc="Processing airports"):
            # check if the airport is already in the airports list
            if airport["icao_code"] in [a.ICAO for a in airports]:
                continue
            # Skip exisitng airports with the same ICAO code
            if Airport.objects.filter(ICAO=airport["icao_code"]).exists():
                continue
            # Check if the icao contains a number to filter most small non-commercial airports
            if any(char.isdigit() for char in airport["icao_code"]):
                continue
            elif airport["iata_code"] == "":
                continue

            # Add tz key and get the timezone from the municipality and country
            try:
                # Ensure lat and lon are to the first decimal place
                latitude = round(float(airport["latitude_deg"]), 1)
                longitude = round(float(airport["longitude_deg"]), 1)
                tz_str = tf.timezone_at(lat=latitude, lng=longitude)
            except KeyError:
                tz_str = "UTC"

            if airport["elevation_ft"] == "":
                airport["elevation_ft"] = None
            airport = Airport(
                ICAO=airport["icao_code"],
                IATA=airport["iata_code"],
                name=airport["name"],
                city=airport["municipality"],
                country=airport["iso_country"],
                elevation=airport["elevation_ft"],
                lat=airport["latitude_deg"],
                lon=airport["longitude_deg"],
                timezone=tz_str,
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

import requests
from django.core.management import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Import airlines from a npow/airline-codes repository"

    def handle(self, *args, **kwargs):
        import json
        from airlines.models import Airline

        airlines = []
        self.stdout.write(f"Importing airlines from airline-codes repository")
        resp = requests.get(
            "https://raw.githubusercontent.com/npow/airline-codes/refs/heads/master/airlines.json"
        )
        airlines_data = json.loads(resp.content.decode("utf-8"))

        for airline in airlines_data:
            if airline["active"] is "Y":
                airline = Airline(
                    ICAO=airline["icao"],
                    IATA=airline["iata"],
                    callsign=airline["callsign"],
                    name=airline["name"],
                    country=airline["country"],
                )
                airlines.append(airline)

        if airlines:
            self.stdout.write("Importing airlines...")
            try:
                Airline.objects.bulk_create(airlines)
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to save airline: {airline}. Error: {e} \n Continuing..."
                    )
                )

            self.stdout.write(self.style.SUCCESS("Successfully imported airlines"))

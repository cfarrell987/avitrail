from datetime import datetime

from django.db import models

from airlines.models import Airline
from airports.models import Airport


class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    departure_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_airport"
    )
    arrival_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrival_airport"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration = models.IntegerField()
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    aircraft = models.CharField(max_length=4)
    distance = models.IntegerField()
    tail_number = models.CharField(max_length=10)

    def calculate_duration(self):
        # Get the timezones of the departure and arrival airports and calculate the difference
        # between the two
        departure_tz = self.departure_airport.timezone
        arrival_tz = self.arrival_airport.timezone
        departure_time = datetime.datetime.strptime(
            self.departure_time, "%Y-%m-%d %H:%M:%S", tzinfo=departure_tz
        )
        arrival_time = datetime.datetime.strptime(
            self.arrival_time, "%Y-%m-%d %H:%M:%S", tzinfo=arrival_tz
        )
        return datetime.timedelta.total_seconds(arrival_time - departure_time)

    def __str__(self):
        return (
            f"{self.flight_number} - {self.departure_airport} to {self.arrival_airport}"
        )


class Seat(models.Model):
    class SeatClass(models.TextChoices):
        ECONOMY = "EC", "Economy"
        ECONOMY_PLUS = "EP", "Economy Plus"
        BUSINESS = "BC", "Business"
        FIRST = "FC", "First"

    seat_number = models.CharField(max_length=4)
    seat_class = models.CharField(max_length=20, choices=SeatClass.choices)
    seat_price = models.DecimalField(max_digits=10, decimal_places=2)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.seat_number} - {self.flight}"

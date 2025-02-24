from random import choices

from django.db import models


class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    departure_airport = models.CharField(max_length=3)
    arrival_airport = models.CharField(max_length=3)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration = models.IntegerField()
    airline = models.CharField(max_length=3)
    aircraft = models.CharField(max_length=4)
    distance = models.IntegerField()
    tail_number = models.CharField(max_length=10)

    def calculate_duration(self):
        return self.arrival_time - self.departure_time

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

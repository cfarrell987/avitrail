from django.db import models
from django.db.models import UniqueConstraint


# Create your models here.


class Airline(models.Model):
    ICAO = models.CharField(max_length=5, null=True)
    IATA = models.CharField(max_length=5, null=True)
    callsign = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)

    UniqueConstraint(name="CODES", fields=["IATA", "ICAO"], nulls_distinct=False)

    def __str__(self):
        return f"{self.ICAO} - {self.name} - {self.country}"

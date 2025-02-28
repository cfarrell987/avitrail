from django.db import models
from django.db.models import UniqueConstraint


class Airport(models.Model):
    ICAO = models.CharField(max_length=4, unique=True)
    IATA = models.CharField(max_length=3, null=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    elevation = models.IntegerField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    timezone = models.CharField(max_length=100, null=True, blank=True)

    UniqueConstraint(name="CODES", fields=["IATA"], nulls_distinct=False)

    def __str__(self):
        return f"{self.ICAO} - {self.name} - {self.city} - {self.country}"

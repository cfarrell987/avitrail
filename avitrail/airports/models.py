from django.contrib.postgres.indexes import GinIndex
from django.core.validators import RegexValidator
from django.db import models

# ICAO location indicators and IATA airport codes are standardized formats —
# see ICAO Doc 7910 and IATA's airport code standard.
ICAO_AIRPORT_CODE_VALIDATOR = RegexValidator(
    regex=r"^[A-Z]{4}$",
    message="ICAO airport codes must be exactly 4 uppercase letters (e.g. KLAX).",
)
IATA_AIRPORT_CODE_VALIDATOR = RegexValidator(
    regex=r"^[A-Z]{3}$",
    message="IATA airport codes must be exactly 3 uppercase letters (e.g. LAX).",
)


class Airport(models.Model):
    ICAO = models.CharField(
        max_length=4, unique=True, validators=[ICAO_AIRPORT_CODE_VALIDATOR]
    )
    IATA = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        unique=True,
        validators=[IATA_AIRPORT_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    elevation = models.IntegerField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    timezone = models.CharField(max_length=100, null=True, blank=True)

    # NULL = active. Set when a re-import no longer finds this airport in the
    # source data (closed/decommissioned) — never deleted outright, since
    # existing flights may reference it and users can still log old flights
    # through it. New flights departing/arriving after this date are blocked
    # at the serializer level (see flights.serializers.FlightSerializer).
    disabled_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        return self.disabled_at is None

    class Meta:
        ordering = ["name"]
        indexes = [
            # Plain B-tree: serves the default ordering above (ORDER BY name).
            models.Index(fields=["name"], name="airport_name_idx"),
            # GIN trigram: accelerates the ILIKE '%term%' substring search
            # SearchFilter runs against name/city — a B-tree index can't help
            # with that access pattern at all.
            GinIndex(
                fields=["name"],
                name="airport_name_trgm_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["city"],
                name="airport_city_trgm_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def save(self, *args, **kwargs):
        # Normalize "no code" to NULL (not '') so multiple airports without
        # an IATA code don't collide under the unique constraint above —
        # Postgres treats NULLs as distinct from each other, unlike ''.
        if self.IATA == "":
            self.IATA = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ICAO} - {self.name} - {self.city} - {self.country}"

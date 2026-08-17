from django.contrib.postgres.indexes import GinIndex
from django.core.validators import RegexValidator
from django.db import models

# ICAO and IATA airline designators are standardized formats — see ICAO
# Doc 8585 (3-letter designators) and IATA's 2-character airline codes,
# which may mix letters and digits (e.g. "9W", "6E").
ICAO_AIRLINE_CODE_VALIDATOR = RegexValidator(
    regex=r"^[A-Z]{3}$",
    message="ICAO airline codes must be exactly 3 uppercase letters (e.g. UAL).",
)
IATA_AIRLINE_CODE_VALIDATOR = RegexValidator(
    regex=r"^[A-Z0-9]{2}$",
    message="IATA airline codes must be exactly 2 uppercase letters and/or digits (e.g. UA, 9W).",
)


class Airline(models.Model):
    ICAO = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        unique=True,
        validators=[ICAO_AIRLINE_CODE_VALIDATOR],
    )
    IATA = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        unique=True,
        validators=[IATA_AIRLINE_CODE_VALIDATOR],
    )
    callsign = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)

    # NULL = active. Set when a re-import finds this airline gone or flagged
    # inactive in the source data — never deleted outright, since existing
    # flights may reference it and users can still log old flights on it.
    # New flights departing after this date are blocked at the serializer
    # level (see flights.serializers.FlightSerializer).
    disabled_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        return self.disabled_at is None

    class Meta:
        ordering = ["name"]
        indexes = [
            # Plain B-tree: serves the default ordering above (ORDER BY name).
            models.Index(fields=["name"], name="airline_name_idx"),
            # GIN trigram: accelerates the ILIKE '%term%' substring search
            # SearchFilter runs against name — a B-tree index can't help
            # with that access pattern at all.
            GinIndex(
                fields=["name"],
                name="airline_name_trgm_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def save(self, *args, **kwargs):
        # Normalize "no code" to NULL (not '') so multiple airlines without
        # a code don't collide under the unique constraints above — Postgres
        # treats NULLs as distinct from each other, unlike ''.
        if self.ICAO == "":
            self.ICAO = None
        if self.IATA == "":
            self.IATA = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ICAO} - {self.name} - {self.country}"

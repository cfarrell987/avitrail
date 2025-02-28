# Generated by Django 5.1.6 on 2025-02-28 16:39

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Airline",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ICAO", models.CharField(max_length=5, null=True)),
                ("IATA", models.CharField(max_length=5, null=True)),
                ("callsign", models.CharField(blank=True, max_length=100, null=True)),
                ("name", models.CharField(max_length=100)),
                ("country", models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]

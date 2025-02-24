# Generated by Django 5.1.6 on 2025-02-23 12:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Flight",
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
                ("flight_number", models.CharField(max_length=10)),
                ("departure_airport", models.CharField(max_length=3)),
                ("arrival_airport", models.CharField(max_length=3)),
                ("departure_time", models.DateTimeField()),
                ("arrival_time", models.DateTimeField()),
                ("duration", models.IntegerField()),
                ("airline", models.CharField(max_length=3)),
                ("aircraft", models.CharField(max_length=4)),
                ("distance", models.IntegerField()),
                ("tail_number", models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name="Seat",
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
                ("seat_number", models.CharField(max_length=4)),
                (
                    "seat_class",
                    models.CharField(
                        choices=[
                            ("EC", "Economy"),
                            ("EP", "Economy Plus"),
                            ("BC", "Business"),
                            ("FC", "First"),
                        ],
                        max_length=20,
                    ),
                ),
                ("seat_price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "flight",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="flights.flight"
                    ),
                ),
            ],
        ),
    ]

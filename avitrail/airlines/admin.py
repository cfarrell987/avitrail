from django.contrib import admin
from airlines.models import Airline


class AirlineAdmin(admin.ModelAdmin):
    list_display = ("name", "ICAO", "IATA", "country")
    search_fields = ("name", "ICAO", "IATA", "country")
    list_filter = ("country",)


admin.site.register(Airline, AirlineAdmin)

from django.contrib import admin
from airlines.models import Airline


class AirlineAdmin(admin.ModelAdmin):
    list_display = ("name", "ICAO", "IATA", "country", "disabled_at")
    search_fields = ("name", "ICAO", "IATA", "country")
    list_filter = ("country", ("disabled_at", admin.EmptyFieldListFilter))


admin.site.register(Airline, AirlineAdmin)

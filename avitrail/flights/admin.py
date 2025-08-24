from django.contrib import admin

from flights.models import Flight, Seat


class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "flight_number",
        "airline",
        "departure_airport",
        "arrival_airport",
        "duration",
    )
    search_fields = (
        "flight_number",
        "airline",
        "departure_time",
        "arrival_time",
        "duration",
        "departure_airport",
        "arrival_airport",
    )
    list_filter = ("flight_number", "tail_number")

    def departure_time(self, obj):
        return obj.departure_time.strftime("%Y-%m-%d %H:%M:%S")

    def arrival_time(self, obj):
        return obj.arrival_time.strftime("%Y-%m-%d %H:%M:%S")

    def duration(self, obj):
        return obj.arrival_time - obj.departure_time

    def seat(self, obj):
        if obj.seat.exists():
            return ", ".join([s.seat_number for s in obj.seat.all()])


class SeatAdmin(admin.ModelAdmin):
    list_display = ("seat_number", "seat_class", "seat_price")
    search_fields = ("seat_number", "seat_class", "seat_price")
    list_filter = ("seat_class", "seat_price")


admin.site.register(Flight, FlightAdmin)
admin.site.register(Seat, SeatAdmin)

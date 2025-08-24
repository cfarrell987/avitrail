from django.contrib import admin

from airports.models import Airport


class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "timezone")
    search_fields = ("name", "city", "country", "timezone")
    list_filter = ("country",)

    def timezone(self, obj):
        return obj.timezone


admin.site.register(Airport, AirportAdmin)

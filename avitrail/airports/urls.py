from django.urls import path

from airports.views import AirportListCreateView

urlpatterns = [
    path("airports/", AirportListCreateView.as_view(), name="airports"),
]

from django.urls import path

from flights.views import FlightListCreateView

urlpatterns = [
    path("flights/", FlightListCreateView.as_view(), name="flights"),
]

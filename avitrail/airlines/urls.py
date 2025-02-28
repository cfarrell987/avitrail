from django.urls import path

from airlines.views import AirlineListCreateView

urlpatterns = [
    path("airlines/", AirlineListCreateView.as_view(), name="airlines"),
]

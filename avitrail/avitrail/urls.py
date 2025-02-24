from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from flights.urls import urlpatterns as flights_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("flights.urls")),
    path("api/auth/", obtain_auth_token, name="api_token"),
    path("flights/", include(flights_urlpatterns)),
]

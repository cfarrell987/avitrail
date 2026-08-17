from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from accounts.views import RegisterView

urlpatterns = [
    path("", obtain_auth_token, name="api_token"),
    path("register/", RegisterView.as_view(), name="register"),
]

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserProfile


class RegistrationTests(APITestCase):
    def test_register_creates_user_and_profile(self):
        url = reverse("register")
        response = self.client.post(
            url,
            {
                "username": "newpilot",
                "email": "newpilot@example.com",
                "password": "S0meStrongPass!",
                "confirmPassword": "S0meStrongPass!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="newpilot")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_register_rejects_mismatched_passwords(self):
        url = reverse("register")
        response = self.client.post(
            url,
            {
                "username": "newpilot2",
                "email": "newpilot2@example.com",
                "password": "S0meStrongPass!",
                "confirmPassword": "different",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="newpilot2").exists())

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existing", email="dup@example.com", password="whatever123"
        )
        url = reverse("register")
        response = self.client.post(
            url,
            {
                "username": "someoneelse",
                "email": "dup@example.com",
                "password": "S0meStrongPass!",
                "confirmPassword": "S0meStrongPass!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Extends the built-in User with billing/subscription info.

    All billing and subscription fields are optional: self-hosted
    deployments have no use for them, and hosted accounts only fill
    them in when they actually subscribe. No raw payment details
    (card numbers etc.) are ever stored here — `payment_customer_id`
    is a reference into an external payment processor (e.g. Stripe),
    which alone is expected to hold PCI-scoped data.
    """

    class SubscriptionPlan(models.TextChoices):
        FREE = "free", "Free"
        PRO = "pro", "Pro"

    class SubscriptionStatus(models.TextChoices):
        NONE = "none", "None"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELED = "canceled", "Canceled"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )

    # Billing address
    billing_name = models.CharField(max_length=150, blank=True)
    billing_address_line1 = models.CharField(max_length=255, blank=True)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(
        max_length=2, blank=True, help_text="ISO 3166-1 alpha-2 country code"
    )

    # Subscription / payment provider linkage
    plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.NONE,
    )
    payment_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="Customer ID from the external payment processor (e.g. Stripe). No card data is stored locally.",
    )
    subscription_current_period_end = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"

from decimal import Decimal
from django.db import models
from django.conf import settings


class BillingPlan(models.Model):
    TIER_CHOICES = [
        ("free", "Free"),
        ("premium", "Premium"),
        ("business", "Business"),
    ]
    DURATION_CHOICES = [
        ("month", "Monthly"),
        ("year", "Yearly"),
    ]
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default="month")
    currency = models.CharField(max_length=3, default="USD")
    stripe_price_id = models.CharField(max_length=255, blank=True)
    paystack_plan_code = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name} ({self.get_tier_display()})"


class PricingTier(models.Model):
    plan = models.ForeignKey(BillingPlan, on_delete=models.CASCADE, related_name="pricing_tiers")
    currency = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=255, blank=True)
    paystack_plan_code = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["plan", "currency"]

    def __str__(self):
        return f"{self.plan.name} ({self.currency} {self.price})"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("canceled", "Canceled"),
        ("past_due", "Past Due"),
        ("expired", "Expired"),
        ("trialing", "Trialing"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(BillingPlan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trialing")
    currency = models.CharField(max_length=3, default="USD")
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    paystack_subscription_code = models.CharField(max_length=255, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.plan} ({self.status})"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("paid", "Paid"),
        ("uncollectible", "Uncollectible"),
        ("void", "Void"),
    ]
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="invoices", null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invoices"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    paystack_invoice_id = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice {self.id} - {self.user} ({self.amount} {self.currency})"


class PaymentGateway(models.Model):
    GATEWAY_CHOICES = [
        ("stripe", "Stripe"),
        ("paystack", "Paystack"),
    ]
    name = models.CharField(max_length=50, choices=GATEWAY_CHOICES, unique=True)
    publishable_key = models.CharField(max_length=512, blank=True)
    secret_key = models.CharField(max_length=512, blank=True)
    webhook_secret = models.CharField(max_length=512, blank=True)
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_name_display()} ({'Test' if self.is_test_mode else 'Live'})"

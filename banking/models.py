from django.db import models
from django.conf import settings


class BankConnectorConfig(models.Model):
    PROVIDER_CHOICES = [
        ("mono", "Mono (Nigeria)"),
        ("plaid", "Plaid (US/CA)"),
        ("truelayer", "Truelayer (UK/EU)"),
    ]
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, unique=True)
    client_id = models.CharField(max_length=255, blank=True)
    client_secret = models.CharField(max_length=255, blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)
    environment = models.CharField(max_length=20, default="sandbox")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_provider_display()} ({self.environment})"


class LinkedBank(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("revoked", "Revoked"),
        ("error", "Error"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="linked_banks"
    )
    provider = models.CharField(max_length=20, choices=BankConnectorConfig.PROVIDER_CHOICES)
    access_token = models.CharField(max_length=512)
    reference = models.CharField(max_length=255, unique=True, db_index=True)
    institution_name = models.CharField(max_length=255, blank=True)
    institution_id = models.CharField(max_length=255, blank=True)
    account_id = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    account_name = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=3, default="NGN")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    last_sync_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.institution_name} - {self.account_name} ({self.user})"


class SyncLog(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]
    linked_bank = models.ForeignKey(
        LinkedBank, on_delete=models.CASCADE, related_name="sync_logs"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transactions_found = models.IntegerField(default=0)
    transactions_created = models.IntegerField(default=0)
    transactions_skipped = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sync {self.linked_bank} - {self.status} ({self.created_at})"

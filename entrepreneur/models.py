from decimal import Decimal
from django.db import models
from django.conf import settings


class Business(models.Model):
    STAGE_CHOICES = [
        ("idea", "Idea Stage"),
        ("validation", "Validation"),
        ("launch", "Ready to Launch"),
        ("operating", "Operating"),
        ("scaling", "Scaling"),
        ("exited", "Exited"),
    ]
    TYPE_CHOICES = [
        ("sole_proprietorship", "Sole Proprietorship"),
        ("llc", "LLC"),
        ("partnership", "Partnership"),
        ("corporation", "Corporation"),
        ("nonprofit", "Non-Profit"),
        ("other", "Other"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="businesses"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    business_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="sole_proprietorship")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default="idea")
    website = models.URLField(blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3, default="NGN")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "businesses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user})"


class BusinessPlan(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="business_plans"
    )
    title = models.CharField(max_length=255, default="Business Plan")
    executive_summary = models.TextField(blank=True)
    mission_statement = models.TextField(blank=True)
    market_analysis = models.TextField(blank=True)
    strategy = models.TextField(blank=True)
    financial_projections = models.JSONField(default=dict, blank=True)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business.name} - {self.title}"


class SideHustle(models.Model):
    PLATFORM_CHOICES = [
        ("freelance", "Freelance"),
        ("ecommerce", "E-Commerce"),
        ("content", "Content Creation"),
        ("gig", "Gig Economy"),
        ("consulting", "Consulting"),
        ("tutoring", "Tutoring"),
        ("other", "Other"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="side_hustles"
    )
    name = models.CharField(max_length=255)
    platform_type = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default="other")
    description = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default="NGN")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user})"


class RevenueStream(models.Model):
    side_hustle = models.ForeignKey(
        SideHustle, on_delete=models.CASCADE, related_name="revenue_streams", null=True, blank=True
    )
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="revenue_streams", null=True, blank=True
    )
    source_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="NGN")
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.source_name}: {self.amount} {self.currency} ({self.date})"


class EntrepreneurshipPath(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    concepts = models.ManyToManyField("education.Concept", related_name="entrepreneurship_paths", blank=True)
    projects = models.ManyToManyField("education.Project", related_name="entrepreneurship_paths", blank=True)
    courses = models.ManyToManyField("education.Course", related_name="entrepreneurship_paths", blank=True)
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title

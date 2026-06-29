from decimal import Decimal
from django.db import models
from django.conf import settings


class FinancialGoal(models.Model):
    CATEGORY_CHOICES = [
        ("emergency_fund", "Emergency Fund"),
        ("debt_payoff", "Debt Payoff"),
        ("savings", "Savings Goal"),
        ("investment", "Investment Target"),
        ("education", "Education Fund"),
        ("retirement", "Retirement"),
        ("home", "Home Purchase"),
        ("business", "Business Capital"),
        ("travel", "Travel"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
        ("abandoned", "Abandoned"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="financial_goals"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="NGN")
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.user} - {self.title} ({self.target_amount} {self.currency})"


class GoalMilestone(models.Model):
    goal = models.ForeignKey(
        FinancialGoal, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    target_date = models.DateField(null=True, blank=True)
    is_reached = models.BooleanField(default=False)
    reached_at = models.DateTimeField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.goal.title} - {self.title}"


class GoalProgress(models.Model):
    goal = models.ForeignKey(
        FinancialGoal, on_delete=models.CASCADE, related_name="progress_log"
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        verbose_name_plural = "Goal progress entries"

    def __str__(self):
        return f"{self.goal} - {self.amount} ({self.recorded_at})"


class LiteracyAssessment(models.Model):
    TOPIC_CHOICES = [
        ("budgeting", "Budgeting"),
        ("saving", "Saving"),
        ("investing", "Investing"),
        ("debt", "Debt Management"),
        ("retirement", "Retirement Planning"),
        ("tax", "Tax Basics"),
        ("insurance", "Insurance"),
        ("credit", "Credit & Loans"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="literacy_assessments"
    )
    topic = models.CharField(max_length=30, choices=TOPIC_CHOICES)
    score = models.IntegerField(help_text="Score out of 100")
    max_score = models.IntegerField(default=100)
    answers = models.JSONField(default=dict, blank=True)
    taken_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-taken_at"]

    def __str__(self):
        return f"{self.user} - {self.get_topic_display()}: {self.score}/{self.max_score}"


class LiteracyLevel(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="literacy_level"
    )
    budgeting = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    saving = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    investing = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    debt = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    retirement = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    overall = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - Overall: {self.get_overall_display()}"

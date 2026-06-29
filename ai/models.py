from django.db import models
from django.conf import settings


class LearningProfile(models.Model):
    PACE_CHOICES = [
        ("slow", "Slow & Thorough"),
        ("moderate", "Moderate"),
        ("fast", "Fast & Concise"),
    ]
    STYLE_CHOICES = [
        ("visual", "Visual"),
        ("reading", "Reading/Writing"),
        ("interactive", "Hands-On/Interactive"),
        ("video", "Video/Watching"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_profile"
    )
    learning_pace = models.CharField(max_length=20, choices=PACE_CHOICES, default="moderate")
    learning_style = models.CharField(max_length=20, choices=STYLE_CHOICES, default="interactive")
    current_difficulty = models.CharField(
        max_length=20,
        choices=[("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced")],
        default="beginner",
    )
    preferred_content_types = models.JSONField(default=list, blank=True)
    topics_of_interest = models.JSONField(default=list, blank=True)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.get_learning_pace_display()} / {self.get_learning_style_display()}"


class UserContext(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_context"
    )
    last_summary = models.JSONField(default=dict, blank=True)
    spending_patterns = models.JSONField(default=dict, blank=True)
    income_patterns = models.JSONField(default=dict, blank=True)
    budget_health = models.JSONField(default=dict, blank=True)
    savings_metrics = models.JSONField(default=dict, blank=True)
    goals_summary = models.JSONField(default=dict, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI Context for {self.user}"


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions"
    )
    title = models.CharField(max_length=255, blank=True, default="Chat")
    messages = models.JSONField(default=list, blank=True)
    context_snapshot = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user} - {self.title} ({self.created_at})"


class Insight(models.Model):
    CATEGORY_CHOICES = [
        ("spending", "Spending Alert"),
        ("savings", "Savings Opportunity"),
        ("budget", "Budget Insight"),
        ("goal", "Goal Progress"),
        ("educational", "Educational Suggestion"),
        ("recommendation", "Recommendation"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="insights"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_category_display()}: {self.title}"


class Recommendation(models.Model):
    RECOMMENDATION_TYPE_CHOICES = [
        ("concept", "Concept"),
        ("project", "Project"),
        ("course", "Course"),
        ("workshop", "Workshop"),
        ("webinar", "Webinar"),
        ("product", "Product"),
        ("learning_path", "Learning Path"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recommendations"
    )
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)
    target_id = models.IntegerField()
    target_title = models.CharField(max_length=255)
    score = models.FloatField(default=0.0)
    reason = models.TextField(blank=True)
    is_clicked = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score", "-created_at"]

    def __str__(self):
        return f"Recommend {self.target_title} for {self.user} (score: {self.score})"


class ConceptExplanation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="concept_explanations"
    )
    concept = models.ForeignKey("education.Concept", on_delete=models.CASCADE)
    explanation = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Explanation of {self.concept} for {self.user}"


class GoalAlignment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goal_alignments"
    )
    goal = models.ForeignKey("goals.FinancialGoal", on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=20, choices=Recommendation.RECOMMENDATION_TYPE_CHOICES)
    target_id = models.IntegerField()
    target_title = models.CharField(max_length=255)
    relevance_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-relevance_score"]

    def __str__(self):
        return f"{self.goal} -> {self.target_title} ({self.relevance_score})"

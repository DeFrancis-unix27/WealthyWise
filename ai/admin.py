from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import (
    LearningProfile, UserContext, ChatSession, Insight,
    Recommendation, ConceptExplanation, GoalAlignment,
)


@admin.register(LearningProfile)
class LearningProfileAdmin(UnfoldModelAdmin):
    list_display = ('user', 'learning_pace', 'learning_style', 'current_difficulty', 'onboarding_completed')
    list_filter = ('learning_pace', 'learning_style', 'current_difficulty', 'onboarding_completed')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserContext)
class UserContextAdmin(UnfoldModelAdmin):
    list_display = ('user', 'last_updated')
    search_fields = ('user__username', 'user__email')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ChatSession)
class ChatSessionAdmin(UnfoldModelAdmin):
    list_display = ('user', 'title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'title')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Insight)
class InsightAdmin(UnfoldModelAdmin):
    list_display = ('user', 'category', 'title', 'is_read', 'is_dismissed', 'created_at')
    list_filter = ('category', 'is_read', 'is_dismissed')
    search_fields = ('user__username', 'title')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Recommendation)
class RecommendationAdmin(UnfoldModelAdmin):
    list_display = ('user', 'recommendation_type', 'target_title', 'score', 'is_clicked')
    list_filter = ('recommendation_type', 'is_clicked')
    search_fields = ('user__username', 'target_title')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ConceptExplanation)
class ConceptExplanationAdmin(UnfoldModelAdmin):
    list_display = ('user', 'concept', 'generated_at')
    search_fields = ('user__username', 'concept__title')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'concept')


@admin.register(GoalAlignment)
class GoalAlignmentAdmin(UnfoldModelAdmin):
    list_display = ('user', 'goal', 'target_title', 'relevance_score')
    search_fields = ('user__username', 'goal__title')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'goal')

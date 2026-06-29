from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import FinancialGoal, GoalMilestone, GoalProgress, LiteracyAssessment, LiteracyLevel


class GoalMilestoneInline(admin.TabularInline):
    model = GoalMilestone
    extra = 0
    readonly_fields = ('is_reached', 'reached_at')


class GoalProgressInline(admin.TabularInline):
    model = GoalProgress
    extra = 0
    readonly_fields = ('recorded_at',)


@admin.register(FinancialGoal)
class FinancialGoalAdmin(UnfoldModelAdmin):
    list_display = ('user', 'title', 'category', 'target_amount', 'current_amount',
                    'currency', 'status', 'target_date')
    list_filter = ('category', 'status', 'currency')
    search_fields = ('user__username', 'title', 'description')
    list_editable = ('status',)
    date_hierarchy = 'target_date'
    inlines = [GoalMilestoneInline, GoalProgressInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(GoalMilestone)
class GoalMilestoneAdmin(UnfoldModelAdmin):
    list_display = ('goal', 'title', 'target_amount', 'target_date', 'is_reached')
    list_filter = ('is_reached',)
    search_fields = ('goal__title', 'title')


@admin.register(GoalProgress)
class GoalProgressAdmin(UnfoldModelAdmin):
    list_display = ('goal', 'amount', 'note', 'recorded_at')
    search_fields = ('goal__title', 'note')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('goal__user')


@admin.register(LiteracyAssessment)
class LiteracyAssessmentAdmin(UnfoldModelAdmin):
    list_display = ('user', 'topic', 'score', 'max_score', 'taken_at')
    list_filter = ('topic',)
    search_fields = ('user__username',)
    date_hierarchy = 'taken_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(LiteracyLevel)
class LiteracyLevelAdmin(UnfoldModelAdmin):
    list_display = ('user', 'budgeting', 'saving', 'investing', 'debt', 'overall')
    list_filter = ('budgeting', 'saving', 'investing', 'debt', 'overall')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

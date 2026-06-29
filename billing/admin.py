from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import BillingPlan, PricingTier, Subscription, Invoice, PaymentGateway


@admin.register(BillingPlan)
class BillingPlanAdmin(UnfoldModelAdmin):
    list_display = ('name', 'tier', 'price', 'currency', 'duration', 'is_active', 'sort_order')
    list_filter = ('tier', 'duration', 'is_active')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name', 'description')


@admin.register(PricingTier)
class PricingTierAdmin(UnfoldModelAdmin):
    list_display = ('plan', 'currency', 'price', 'is_active')
    list_filter = ('currency', 'is_active')
    list_editable = ('is_active',)


@admin.register(Subscription)
class SubscriptionAdmin(UnfoldModelAdmin):
    list_display = ('user', 'plan', 'status', 'currency', 'start_date', 'end_date', 'auto_renew')
    list_filter = ('status', 'plan', 'auto_renew')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('start_date', 'end_date', 'created_at', 'updated_at')
    date_hierarchy = 'start_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plan')


@admin.register(Invoice)
class InvoiceAdmin(UnfoldModelAdmin):
    list_display = ('id', 'user', 'amount', 'currency', 'status', 'due_date', 'paid_at')
    list_filter = ('status', 'currency')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'due_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(UnfoldModelAdmin):
    list_display = ('name', 'is_active', 'is_test_mode')
    list_filter = ('is_active', 'is_test_mode')

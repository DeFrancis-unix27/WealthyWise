from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import (
    ProductCategory, Product, CuratedCollection, Order, OrderItem,
    AffiliatePartner, AffiliateLink, ServiceReferral, Commission, Payout,
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(UnfoldModelAdmin):
    list_display = ('name', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(UnfoldModelAdmin):
    list_display = ('title', 'product_type', 'category', 'price', 'currency', 'is_active', 'featured', 'sort_order')
    list_filter = ('product_type', 'is_active', 'featured')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'featured', 'sort_order')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(CuratedCollection)
class CuratedCollectionAdmin(UnfoldModelAdmin):
    list_display = ('title', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    prepopulated_fields = {'slug': ('title',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'currency')


@admin.register(Order)
class OrderAdmin(UnfoldModelAdmin):
    list_display = ('id', 'user', 'total', 'currency', 'status', 'paid_at', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AffiliatePartner)
class AffiliatePartnerAdmin(UnfoldModelAdmin):
    list_display = ('name', 'commission_type', 'commission_value', 'commission_currency',
                    'is_service_provider', 'status')
    list_filter = ('commission_type', 'is_service_provider', 'status')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(UnfoldModelAdmin):
    list_display = ('partner', 'code', 'clicks', 'conversions', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('partner__name', 'code')


@admin.register(ServiceReferral)
class ServiceReferralAdmin(UnfoldModelAdmin):
    list_display = ('affiliate_link', 'service_name', 'status', 'commission_earned', 'signed_up_at')
    list_filter = ('status',)
    search_fields = ('service_name', 'affiliate_link__partner__name')


@admin.register(Commission)
class CommissionAdmin(UnfoldModelAdmin):
    list_display = ('affiliate_link', 'amount', 'currency', 'status', 'paid_at')
    list_filter = ('status',)
    search_fields = ('affiliate_link__partner__name',)


@admin.register(Payout)
class PayoutAdmin(UnfoldModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'processed_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

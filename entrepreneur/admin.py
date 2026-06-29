from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import Business, BusinessPlan, SideHustle, RevenueStream, EntrepreneurshipPath


class RevenueStreamInline(admin.TabularInline):
    model = RevenueStream
    extra = 0


@admin.register(Business)
class BusinessAdmin(UnfoldModelAdmin):
    list_display = ('name', 'user', 'business_type', 'stage', 'currency', 'is_active')
    list_filter = ('business_type', 'stage', 'is_active')
    search_fields = ('name', 'user__username', 'user__email')
    list_editable = ('is_active',)
    inlines = [RevenueStreamInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(BusinessPlan)
class BusinessPlanAdmin(UnfoldModelAdmin):
    list_display = ('business', 'title', 'is_complete', 'created_at')
    list_filter = ('is_complete',)
    search_fields = ('business__name', 'title')


@admin.register(SideHustle)
class SideHustleAdmin(UnfoldModelAdmin):
    list_display = ('name', 'user', 'platform_type', 'is_active', 'created_at')
    list_filter = ('platform_type', 'is_active')
    search_fields = ('name', 'user__username')
    inlines = [RevenueStreamInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(RevenueStream)
class RevenueStreamAdmin(UnfoldModelAdmin):
    list_display = ('source_name', 'amount', 'currency', 'date', 'side_hustle', 'business')
    list_filter = ('currency',)
    search_fields = ('source_name',)
    date_hierarchy = 'date'


@admin.register(EntrepreneurshipPath)
class EntrepreneurshipPathAdmin(UnfoldModelAdmin):
    list_display = ('title', 'is_premium', 'is_published', 'sort_order')
    list_filter = ('is_premium', 'is_published')
    search_fields = ('title', 'description')
    list_editable = ('is_premium', 'is_published', 'sort_order')
    prepopulated_fields = {'slug': ('title',)}

from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import BankConnectorConfig, LinkedBank, SyncLog


@admin.register(BankConnectorConfig)
class BankConnectorConfigAdmin(UnfoldModelAdmin):
    list_display = ('provider', 'environment', 'is_active', 'created_at')
    list_filter = ('provider', 'environment', 'is_active')
    search_fields = ('provider',)


@admin.register(LinkedBank)
class LinkedBankAdmin(UnfoldModelAdmin):
    list_display = ('user', 'provider', 'institution_name', 'account_name',
                    'currency', 'status', 'last_sync_at')
    list_filter = ('provider', 'status', 'currency')
    search_fields = ('user__username', 'user__email', 'institution_name', 'account_name')
    readonly_fields = ('access_token', 'reference', 'created_at', 'updated_at')
    date_hierarchy = 'last_sync_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SyncLog)
class SyncLogAdmin(UnfoldModelAdmin):
    list_display = ('linked_bank', 'status', 'transactions_found',
                    'transactions_created', 'started_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('linked_bank__institution_name', 'linked_bank__user__username')
    readonly_fields = ('started_at', 'completed_at', 'created_at')
    date_hierarchy = 'created_at'

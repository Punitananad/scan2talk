"""
Admin configuration for communications app.
"""
from django.contrib import admin
from .models import CommunicationProvider, CommunicationLog


@admin.register(CommunicationProvider)
class CommunicationProviderAdmin(admin.ModelAdmin):
    """Communication provider admin."""
    
    list_display = [
        'name', 'provider_type', 'is_active',
        'daily_usage', 'monthly_usage', 'last_test_success'
    ]
    list_filter = ['provider_type', 'is_active', 'last_test_success']
    search_fields = ['name', 'configuration']
    readonly_fields = [
        'daily_usage', 'monthly_usage', 'last_reset_date',
        'last_test_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'provider_type', 'is_active')
        }),
        ('Configuration', {
            'fields': ('configuration',),
            'description': 'Provider-specific configuration (API keys, etc.)'
        }),
        ('Limits', {
            'fields': ('daily_limit', 'monthly_limit', 'rate_limit_per_minute')
        }),
        ('Usage Tracking', {
            'fields': ('daily_usage', 'monthly_usage', 'last_reset_date'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('last_test_at', 'last_test_success', 'last_error'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    """Communication log admin."""
    
    list_display = [
        'channel', 'recipient', 'status', 'created_at',
        'sent_at', 'retry_count'
    ]
    list_filter = ['channel', 'status', 'created_at']
    search_fields = [
        'recipient', 'message_content', 'external_id',
        'error_message'
    ]
    readonly_fields = [
        'created_at', 'sent_at', 'delivered_at', 'failed_at'
    ]
    
    fieldsets = (
        ('Message Details', {
            'fields': ('provider', 'channel', 'recipient', 'message_content')
        }),
        ('Status', {
            'fields': ('status', 'external_id', 'retry_count')
        }),
        ('Timing', {
            'fields': ('created_at', 'sent_at', 'delivered_at', 'failed_at')
        }),
        ('Error Information', {
            'fields': ('error_code', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Cost Tracking', {
            'fields': ('cost_amount', 'cost_currency'),
            'classes': ('collapse',)
        }),
        ('Provider Response', {
            'fields': ('provider_response',),
            'classes': ('collapse',)
        }),
    )
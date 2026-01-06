"""
Admin configuration for routing app.
"""
from django.contrib import admin
from .models import RoutingRule, BlockedContact, CommunicationTemplate, RoutingLog


@admin.register(RoutingRule)
class RoutingRuleAdmin(admin.ModelAdmin):
    """Routing rule admin."""
    
    list_display = [
        'name', 'gateway', 'priority', 'emergency_only',
        'is_active', 'created_at'
    ]
    list_filter = [
        'emergency_only', 'emergency_escalation', 'require_approval',
        'is_active', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'gateway__title', 'gateway__owner__email'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('gateway', 'name', 'description', 'priority')
        }),
        ('Conditions', {
            'fields': (
                'allowed_channels', 'allowed_intents',
                'time_window_start', 'time_window_end', 'allowed_days'
            )
        }),
        ('Rate Limiting', {
            'fields': ('max_requests_per_hour', 'max_requests_per_day')
        }),
        ('Emergency Settings', {
            'fields': ('emergency_only', 'emergency_escalation')
        }),
        ('Actions', {
            'fields': ('forward_to_channels', 'auto_response_message', 'require_approval')
        }),
        ('System', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlockedContact)
class BlockedContactAdmin(admin.ModelAdmin):
    """Blocked contact admin."""
    
    list_display = [
        'gateway', 'block_type', 'value', 'blocked_by', 'created_at'
    ]
    list_filter = ['block_type', 'created_at']
    search_fields = [
        'value', 'reason', 'gateway__title', 'blocked_by__email'
    ]
    readonly_fields = ['created_at']


@admin.register(CommunicationTemplate)
class CommunicationTemplateAdmin(admin.ModelAdmin):
    """Communication template admin."""
    
    list_display = [
        'name', 'gateway', 'template_type', 'is_active', 'created_at'
    ]
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = [
        'name', 'subject', 'message', 'gateway__title'
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RoutingLog)
class RoutingLogAdmin(admin.ModelAdmin):
    """Routing log admin."""
    
    list_display = [
        'gateway', 'channel', 'intent', 'action_taken',
        'success', 'processing_time_ms', 'created_at'
    ]
    list_filter = ['channel', 'intent', 'action_taken', 'success', 'created_at']
    search_fields = [
        'gateway__title', 'ip_address', 'error_message'
    ]
    readonly_fields = ['created_at']
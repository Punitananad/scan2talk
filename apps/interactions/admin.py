"""
Admin configuration for interactions app.
"""
from django.contrib import admin
from .models import (
    InteractionSession, InteractionLog, CommunicationAttempt,
    InteractionFeedback, InteractionAnalytics
)


@admin.register(InteractionSession)
class InteractionSessionAdmin(admin.ModelAdmin):
    """Interaction session admin."""
    
    list_display = [
        'session_token', 'gateway', 'channel', 'intent',
        'status', 'expires_at', 'created_at'
    ]
    list_filter = ['channel', 'intent', 'status', 'created_at']
    search_fields = [
        'session_token', 'gateway__title', 'ip_address', 'message'
    ]
    readonly_fields = ['session_token', 'created_at', 'updated_at']


@admin.register(InteractionLog)
class InteractionLogAdmin(admin.ModelAdmin):
    """Interaction log admin."""
    
    list_display = [
        'gateway', 'channel_used', 'intent', 'initiated_at',
        'success', 'was_blocked', 'response_sent'
    ]
    list_filter = [
        'channel_used', 'intent', 'success', 'was_blocked',
        'response_sent', 'initiated_at'
    ]
    search_fields = [
        'gateway__title', 'message_content', 'ip_address',
        'error_message', 'response_message'
    ]
    readonly_fields = ['id', 'initiated_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('gateway', 'session', 'channel_used', 'intent')
        }),
        ('Content', {
            'fields': ('message_content', 'response_message')
        }),
        ('Timing', {
            'fields': ('initiated_at', 'completed_at', 'duration_seconds')
        }),
        ('Status', {
            'fields': ('success', 'was_blocked', 'block_reason', 'error_message')
        }),
        ('Client Information', {
            'fields': ('ip_address', 'user_agent', 'metadata')
        }),
        ('Response', {
            'fields': ('response_sent', 'response_channel')
        }),
    )


@admin.register(CommunicationAttempt)
class CommunicationAttemptAdmin(admin.ModelAdmin):
    """Communication attempt admin."""
    
    list_display = [
        'interaction_log', 'channel', 'recipient', 'status',
        'sent_at', 'provider_name'
    ]
    list_filter = ['channel', 'status', 'provider_name', 'created_at']
    search_fields = [
        'recipient', 'message_content', 'external_id',
        'error_message', 'interaction_log__gateway__title'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'sent_at',
        'delivered_at', 'failed_at'
    ]


@admin.register(InteractionFeedback)
class InteractionFeedbackAdmin(admin.ModelAdmin):
    """Interaction feedback admin."""
    
    list_display = [
        'interaction_log', 'feedback_type', 'blocked_contact',
        'forwarded_to_support', 'created_at'
    ]
    list_filter = [
        'feedback_type', 'blocked_contact',
        'forwarded_to_support', 'created_at'
    ]
    search_fields = [
        'notes', 'interaction_log__gateway__title'
    ]
    readonly_fields = ['created_at']


@admin.register(InteractionAnalytics)
class InteractionAnalyticsAdmin(admin.ModelAdmin):
    """Interaction analytics admin."""
    
    list_display = [
        'gateway', 'date', 'total_interactions',
        'successful_interactions', 'blocked_interactions'
    ]
    list_filter = ['date', 'gateway__context_type']
    search_fields = ['gateway__title', 'gateway__owner__email']
    readonly_fields = ['created_at']
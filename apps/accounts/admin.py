"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserSession, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin."""
    
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'role', 'is_verified', 'is_active', 'created_at'
    ]
    list_filter = [
        'role', 'is_verified', 'is_active', 'subscription_tier', 'created_at'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'company_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Business Information', {
            'fields': ('role', 'company_name', 'business_registration')
        }),
        ('Verification', {
            'fields': ('is_verified', 'is_phone_verified')
        }),
        ('Subscription', {
            'fields': ('subscription_tier', 'gateway_limit', 'monthly_interaction_limit')
        }),
        ('Security', {
            'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin."""
    
    list_display = ['user', 'timezone', 'language', 'public_profile', 'created_at']
    list_filter = ['timezone', 'language', 'public_profile', 'email_notifications']
    search_fields = ['user__email', 'user__username', 'bio']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """User session admin."""
    
    list_display = ['user', 'ip_address', 'is_active', 'created_at', 'last_activity']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'ip_address', 'location']
    readonly_fields = ['created_at', 'last_activity']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Login attempt admin."""
    
    list_display = ['email', 'ip_address', 'success', 'failure_reason', 'created_at']
    list_filter = ['success', 'created_at']
    search_fields = ['email', 'ip_address']
    readonly_fields = ['created_at']
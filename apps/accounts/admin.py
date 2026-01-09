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



# Wallet Admin
from .wallet_models import Wallet, WalletTransaction, RechargeOrder


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Wallet admin with management actions."""
    
    list_display = ['user', 'balance', 'call_credits', 'total_recharged', 'total_spent', 'is_active', 'is_frozen']
    list_filter = ['is_active', 'is_frozen', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'last_recharge_at', 'last_transaction_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Balance', {
            'fields': ('balance', 'call_credits')
        }),
        ('Statistics', {
            'fields': ('total_recharged', 'total_spent', 'total_calls_made')
        }),
        ('Status', {
            'fields': ('is_active', 'is_frozen', 'frozen_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_recharge_at', 'last_transaction_at')
        }),
    )
    
    actions = ['freeze_wallets', 'unfreeze_wallets']
    
    def freeze_wallets(self, request, queryset):
        for wallet in queryset:
            wallet.freeze('Frozen by admin')
        self.message_user(request, f'{queryset.count()} wallets frozen')
    freeze_wallets.short_description = 'Freeze selected wallets'
    
    def unfreeze_wallets(self, request, queryset):
        for wallet in queryset:
            wallet.unfreeze()
        self.message_user(request, f'{queryset.count()} wallets unfrozen')
    unfreeze_wallets.short_description = 'Unfreeze selected wallets'


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """Wallet transaction admin."""
    
    list_display = ['wallet', 'transaction_type', 'amount', 'balance_after', 'credits_after', 'payment_status', 'created_at']
    list_filter = ['transaction_type', 'payment_status', 'created_at']
    search_fields = ['wallet__user__email', 'payment_id', 'reference']
    readonly_fields = ['created_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction', {
            'fields': ('wallet', 'transaction_type', 'amount', 'balance_after', 'credits_after')
        }),
        ('Payment', {
            'fields': ('payment_id', 'payment_method', 'payment_status')
        }),
        ('Details', {
            'fields': ('reference', 'notes')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )


@admin.register(RechargeOrder)
class RechargeOrderAdmin(admin.ModelAdmin):
    """Recharge order admin with manual completion."""
    
    list_display = ['order_id', 'user', 'amount', 'credits_to_add', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'user__email', 'gateway_order_id', 'gateway_payment_id']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order', {
            'fields': ('user', 'wallet', 'order_id', 'amount', 'credits_to_add')
        }),
        ('Gateway', {
            'fields': ('gateway_order_id', 'gateway_payment_id', 'gateway_signature')
        }),
        ('Status', {
            'fields': ('status', 'failure_reason')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at', 'expires_at')
        }),
    )
    
    actions = ['mark_completed', 'mark_failed']
    
    def mark_completed(self, request, queryset):
        count = 0
        for order in queryset.filter(status__in=['created', 'pending']):
            order.mark_completed()
            count += 1
        self.message_user(request, f'{count} orders marked as completed and credited')
    mark_completed.short_description = 'Mark as completed (manual credit)'
    
    def mark_failed(self, request, queryset):
        count = 0
        for order in queryset.filter(status__in=['created', 'pending']):
            order.mark_failed('Manually failed by admin')
            count += 1
        self.message_user(request, f'{count} orders marked as failed')
    mark_failed.short_description = 'Mark as failed'

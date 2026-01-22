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
        'role', 'is_verified', 'is_distributor', 'distributor_verified', 'is_active', 'created_at'
    ]
    list_filter = [
        'role', 'is_verified', 'is_active', 'subscription_tier', 'is_distributor', 'distributor_verified', 'created_at'
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
        ('Distributor', {
            'fields': ('is_distributor', 'distributor_verified', 'distributor_registered_at')
        }),
        ('Subscription', {
            'fields': ('subscription_tier', 'gateway_limit', 'monthly_interaction_limit')
        }),
        ('Security', {
            'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip', 'distributor_registered_at']
    
    actions = ['verify_distributors', 'assign_password_to_distributors']
    
    def verify_distributors(self, request, queryset):
        """Verify selected distributors."""
        count = 0
        for user in queryset.filter(is_distributor=True, distributor_verified=False):
            user.distributor_verified = True
            user.save()
            count += 1
        self.message_user(request, f'{count} distributors verified. Remember to assign passwords!')
    verify_distributors.short_description = 'Verify selected distributors'
    
    def assign_password_to_distributors(self, request, queryset):
        """Assign random password to distributors."""
        import secrets
        import string
        
        count = 0
        passwords = []
        for user in queryset.filter(is_distributor=True):
            # Generate random password
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            user.set_password(password)
            user.save()
            
            passwords.append({
                'username': user.username,
                'email': user.email,
                'phone': user.get_decrypted_phone(),
                'password': password
            })
            count += 1
        
        # Show passwords in message (in production, send via SMS/Email)
        if passwords:
            msg = f'Assigned passwords to {count} distributors:\n\n'
            for p in passwords:
                msg += f"Phone: {p['phone']} | Password: {p['password']}\n"
            self.message_user(request, msg)
    assign_password_to_distributors.short_description = 'Assign random passwords to distributors'


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



# Recharge Models Admin
from .recharge_models import RechargeCategory, RechargePlan, QRWallet, QRWalletTransaction, VisitorPayment, DistributorPayment


@admin.register(RechargeCategory)
class RechargeCategoryAdmin(admin.ModelAdmin):
    """Recharge category admin."""
    
    list_display = ['name', 'category_type', 'distributor_activation_fee', 'message_cost', 'call_cost_per_minute', 'is_active', 'is_default']
    list_filter = ['category_type', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category_type', 'description', 'is_active', 'is_default')
        }),
        ('Free Usage Limits', {
            'fields': ('free_messages_limit', 'free_calls_limit'),
            'description': 'For trial/free categories'
        }),
        ('Pricing', {
            'fields': ('message_cost', 'call_cost_per_minute'),
            'description': 'For prepaid/postpaid categories'
        }),
        ('Distributor Settings', {
            'fields': ('distributor_activation_fee',),
            'description': 'One-time payment for distributor category'
        }),
        ('Display', {
            'fields': ('color', 'icon')
        }),
    )


@admin.register(RechargePlan)
class RechargePlanAdmin(admin.ModelAdmin):
    """Recharge plan admin."""
    
    list_display = ['name', 'amount', 'message_credits', 'call_minutes', 'validity_days', 'is_popular', 'is_active']
    list_filter = ['is_popular', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['display_order', '-amount']


@admin.register(QRWallet)
class QRWalletAdmin(admin.ModelAdmin):
    """QR Wallet admin."""
    
    list_display = ['qr_code', 'category', 'balance', 'message_credits', 'call_minutes', 'is_active', 'is_suspended']
    list_filter = ['category', 'is_active', 'is_suspended']
    search_fields = ['qr_code__qr_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('QR Code', {
            'fields': ('qr_code', 'category')
        }),
        ('Balance & Credits', {
            'fields': ('balance', 'message_credits', 'call_minutes')
        }),
        ('Usage Statistics', {
            'fields': ('total_messages_sent', 'total_calls_made', 'total_call_duration', 'free_messages_used', 'free_calls_used')
        }),
        ('Status', {
            'fields': ('is_active', 'is_suspended', 'suspension_reason')
        }),
        ('Auto-Recharge', {
            'fields': ('auto_recharge_enabled', 'auto_recharge_plan', 'auto_recharge_threshold')
        }),
    )


@admin.register(QRWalletTransaction)
class QRWalletTransactionAdmin(admin.ModelAdmin):
    """QR Wallet transaction admin."""
    
    list_display = ['wallet', 'transaction_type', 'amount', 'message_credits', 'call_minutes', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__qr_code__qr_code', 'reference_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(VisitorPayment)
class VisitorPaymentAdmin(admin.ModelAdmin):
    """Visitor payment admin."""
    
    list_display = ['qr_code', 'amount', 'payment_type', 'status', 'communication_sent', 'created_at']
    list_filter = ['payment_type', 'status', 'communication_sent', 'created_at']
    search_fields = ['qr_code__qr_code', 'order_id', 'visitor_phone']
    readonly_fields = ['created_at', 'updated_at', 'communication_sent_at']
    date_hierarchy = 'created_at'


@admin.register(DistributorPayment)
class DistributorPaymentAdmin(admin.ModelAdmin):
    """Distributor payment admin - one-time activation payments."""
    
    list_display = ['qr_code', 'amount', 'status', 'phone', 'paid_at', 'created_at']
    list_filter = ['status', 'created_at', 'paid_at']
    search_fields = ['qr_code__qr_code', 'order_id', 'phone', 'gateway_payment_id']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('QR Code', {
            'fields': ('qr_code',)
        }),
        ('Payment Details', {
            'fields': ('amount', 'status', 'phone')
        }),
        ('Gateway Info', {
            'fields': ('order_id', 'gateway_order_id', 'gateway_payment_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at')
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        """Manually mark payments as completed."""
        count = 0
        for payment in queryset.filter(status='pending'):
            payment.mark_completed('MANUAL_ADMIN')
            count += 1
        self.message_user(request, f'{count} payments marked as completed')
    mark_as_completed.short_description = 'Mark as completed (manual)'
    
    def mark_as_failed(self, request, queryset):
        """Manually mark payments as failed."""
        count = 0
        for payment in queryset.filter(status='pending'):
            payment.mark_failed()
            count += 1
        self.message_user(request, f'{count} payments marked as failed')
    mark_as_failed.short_description = 'Mark as failed'

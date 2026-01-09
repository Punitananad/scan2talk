"""
Admin configuration for gateways app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Gateway, EntryPoint, GatewaySettings, GatewayAnalytics
from .qr_models import PreGeneratedQR, QRBatch


@admin.register(PreGeneratedQR)
class PreGeneratedQRAdmin(admin.ModelAdmin):
    """Pre-generated QR code admin."""
    
    list_display = [
        'qr_code', 'status', 'service_mode', 'wallet_enabled', 'owner', 'batch_number',
        'access_count', 'activated_at', 'created_at', 'qr_image_preview'
    ]
    list_filter = ['status', 'service_mode', 'wallet_enabled', 'direct_service_enabled', 'activated_by_admin', 'batch_number', 'created_at']
    search_fields = ['qr_code', 'owner__email', 'batch_number', 'notes']
    readonly_fields = [
        'id', 'qr_code', 'activation_token', 'qr_image_preview',
        'access_count', 'last_accessed_at', 'activated_at', 'created_at', 'updated_at',
        'activation_url_display', 'access_url_display'
    ]
    
    fieldsets = (
        ('QR Code Information', {
            'fields': ('qr_code', 'qr_image_preview', 'status', 'batch_number')
        }),
        ('Service Configuration (Admin Control)', {
            'fields': ('service_mode', 'wallet_enabled', 'direct_service_enabled'),
            'description': 'Control whether this QR uses wallet service (paid), direct service (free), or both'
        }),
        ('Ownership', {
            'fields': ('owner', 'gateway', 'activated_at', 'activated_by_admin')
        }),
        ('URLs', {
            'fields': ('activation_url_display', 'access_url_display')
        }),
        ('Tracking', {
            'fields': ('access_count', 'last_accessed_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('notes', 'expires_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': ('activation_token',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_available', 'mark_as_expired', 'enable_wallet_service', 'disable_wallet_service', 'enable_both_services']
    
    def qr_image_preview(self, obj):
        if obj.qr_image:
            return format_html('<img src="{}" width="150" height="150" />', obj.qr_image.url)
        return "No image"
    qr_image_preview.short_description = 'QR Code Image'
    
    def activation_url_display(self, obj):
        url = obj.get_activation_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)
    activation_url_display.short_description = 'Activation URL'
    
    def access_url_display(self, obj):
        url = obj.get_access_url()
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)
    access_url_display.short_description = 'Access URL'
    
    def mark_as_available(self, request, queryset):
        queryset.update(status='available', owner=None, gateway=None)
        self.message_user(request, f'{queryset.count()} QR codes marked as available')
    mark_as_available.short_description = 'Mark selected as available'
    
    def mark_as_expired(self, request, queryset):
        queryset.update(status='expired')
        self.message_user(request, f'{queryset.count()} QR codes marked as expired')
    mark_as_expired.short_description = 'Mark selected as expired'
    
    def enable_wallet_service(self, request, queryset):
        """Enable wallet service for selected QR codes."""
        queryset.update(service_mode='wallet', wallet_enabled=True, direct_service_enabled=False)
        self.message_user(request, f'{queryset.count()} QR codes set to wallet service (paid calls)')
    enable_wallet_service.short_description = 'Enable wallet service (paid)'
    
    def disable_wallet_service(self, request, queryset):
        """Disable wallet service for selected QR codes."""
        queryset.update(service_mode='direct', wallet_enabled=False, direct_service_enabled=True)
        self.message_user(request, f'{queryset.count()} QR codes set to direct service (free)')
    disable_wallet_service.short_description = 'Enable direct service (free)'
    
    def enable_both_services(self, request, queryset):
        """Enable both wallet and direct service."""
        queryset.update(service_mode='both', wallet_enabled=True, direct_service_enabled=True)
        self.message_user(request, f'{queryset.count()} QR codes set to both services')
    enable_both_services.short_description = 'Enable both services'


@admin.register(QRBatch)
class QRBatchAdmin(admin.ModelAdmin):
    """QR Batch admin."""
    
    list_display = [
        'batch_number', 'quantity', 'available_count',
        'activated_count', 'reserved_count', 'created_by', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['batch_number', 'purpose', 'notes', 'created_by__email']
    readonly_fields = [
        'id', 'batch_number', 'quantity', 'activated_count',
        'reserved_count', 'available_count', 'created_at'
    ]
    
    fieldsets = (
        ('Batch Information', {
            'fields': ('batch_number', 'quantity', 'purpose', 'notes')
        }),
        ('Statistics', {
            'fields': ('available_count', 'reserved_count', 'activated_count')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at')
        }),
    )
    
    actions = ['update_batch_statistics']
    
    def update_batch_statistics(self, request, queryset):
        for batch in queryset:
            batch.update_statistics()
        self.message_user(request, f'Updated statistics for {queryset.count()} batches')
    update_batch_statistics.short_description = 'Update batch statistics'


@admin.register(Gateway)
class GatewayAdmin(admin.ModelAdmin):
    """Gateway admin."""
    
    list_display = [
        'title', 'owner', 'context_type', 'location_name',
        'total_interactions', 'is_active', 'created_at'
    ]
    list_filter = [
        'context_type', 'is_active', 'is_emergency_enabled',
        'auto_response_enabled', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'location_name', 'identifier_text',
        'owner__email', 'owner__username'
    ]
    readonly_fields = [
        'id', 'total_interactions', 'last_interaction_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'title', 'description', 'context_type')
        }),
        ('Identification', {
            'fields': ('location_name', 'identifier_text')
        }),
        ('Settings', {
            'fields': ('is_emergency_enabled', 'auto_response_enabled', 'auto_response_message')
        }),
        ('Analytics', {
            'fields': ('total_interactions', 'last_interaction_at'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EntryPoint)
class EntryPointAdmin(admin.ModelAdmin):
    """Entry point admin."""
    
    list_display = [
        'gateway', 'type', 'public_identifier',
        'access_count', 'is_active', 'created_at'
    ]
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = [
        'public_identifier', 'phone_number',
        'gateway__title', 'gateway__owner__email'
    ]
    readonly_fields = [
        'id', 'public_identifier', 'access_count',
        'last_accessed_at', 'created_at', 'updated_at'
    ]


@admin.register(GatewaySettings)
class GatewaySettingsAdmin(admin.ModelAdmin):
    """Gateway settings admin."""
    
    list_display = [
        'gateway', 'max_interactions_per_day',
        'log_interactions', 'store_contact_info'
    ]
    list_filter = ['log_interactions', 'store_contact_info', 'timezone']
    search_fields = ['gateway__title', 'gateway__owner__email']


@admin.register(GatewayAnalytics)
class GatewayAnalyticsAdmin(admin.ModelAdmin):
    """Gateway analytics admin."""
    
    list_display = [
        'gateway', 'date', 'total_interactions',
        'successful_interactions', 'blocked_interactions'
    ]
    list_filter = ['date', 'gateway__context_type']
    search_fields = ['gateway__title', 'gateway__owner__email']
    readonly_fields = ['created_at']
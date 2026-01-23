"""
Django admin configuration for core app.
"""
from django.contrib import admin
from .pricing_models import PricingSettings
from .models import TagOrder


@admin.register(PricingSettings)
class PricingSettingsAdmin(admin.ModelAdmin):
    """Admin interface for centralized pricing settings."""
    
    list_display = ['tag_price', 'distributor_activation_fee', 'updated_at', 'updated_by']
    readonly_fields = ['updated_at', 'updated_by']
    
    fieldsets = (
        ('Physical Tag Pricing', {
            'fields': ('tag_price',),
            'description': 'Set the price for physical QR tags sold to customers'
        }),
        ('Distributor Pricing', {
            'fields': ('distributor_activation_fee',),
            'description': 'Set the one-time activation fee for distributor category QR codes'
        }),
        ('Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Only allow one instance."""
        return not PricingSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of pricing settings."""
        return False
    
    def save_model(self, request, obj, form, change):
        """Save with user tracking."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TagOrder)
class TagOrderAdmin(admin.ModelAdmin):
    """Admin interface for tag orders."""
    
    list_display = ['order_id', 'name', 'phone', 'quantity', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'name', 'phone', 'email']
    readonly_fields = ['order_id', 'created_at', 'updated_at', 'shipped_at', 'delivered_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status', 'quantity', 'total_amount')
        }),
        ('Customer Details', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Delivery Address', {
            'fields': ('address', 'city', 'state', 'pincode')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

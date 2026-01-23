"""
Centralized Pricing Settings Model
"""
from django.db import models
from django.core.cache import cache


class PricingSettings(models.Model):
    """
    Centralized pricing configuration - Single instance model
    """
    # Physical Tag Pricing
    tag_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=499.00,
        help_text="Price for physical QR tag (₹)"
    )
    
    # Distributor Activation Fee
    distributor_activation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500.00,
        help_text="One-time activation fee for distributor category (₹)"
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pricing_updates'
    )
    
    class Meta:
        db_table = 'pricing_settings'
        verbose_name = 'Pricing Settings'
        verbose_name_plural = 'Pricing Settings'
    
    def __str__(self):
        return f"Pricing Settings (Tag: ₹{self.tag_price}, Distributor: ₹{self.distributor_activation_fee})"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and PricingSettings.objects.exists():
            raise ValueError('Only one PricingSettings instance is allowed')
        
        super().save(*args, **kwargs)
        
        # Clear cache when settings are updated
        cache.delete('pricing_settings')
        
        # Update distributor categories
        self.update_distributor_categories()
    
    def update_distributor_categories(self):
        """Update all distributor categories with new fee"""
        from apps.accounts.recharge_models import RechargeCategory
        
        RechargeCategory.objects.filter(
            category_type='distributor'
        ).update(
            distributor_activation_fee=self.distributor_activation_fee
        )
    
    @classmethod
    def get_settings(cls):
        """Get or create pricing settings (cached)"""
        settings = cache.get('pricing_settings')
        
        if settings is None:
            settings, created = cls.objects.get_or_create(
                pk=1,
                defaults={
                    'tag_price': 499.00,
                    'distributor_activation_fee': 500.00
                }
            )
            cache.set('pricing_settings', settings, 3600)  # Cache for 1 hour
        
        return settings
    
    @classmethod
    def get_tag_price(cls):
        """Get current tag price"""
        return cls.get_settings().tag_price
    
    @classmethod
    def get_distributor_fee(cls):
        """Get current distributor activation fee"""
        return cls.get_settings().distributor_activation_fee

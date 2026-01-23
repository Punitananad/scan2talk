"""
Gateway and entry point models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone as django_timezone
from apps.core.models import BaseModel
from apps.core.utils import generate_short_code, generate_qr_code

# Import QR models
from .qr_models import PreGeneratedQR, QRBatch


class Gateway(BaseModel):
    """
    Main gateway model representing a communication endpoint.
    """
    CONTEXT_CHOICES = [
        ('vehicle', 'Vehicle'),
        ('home', 'Home/Property'),
        ('office', 'Office/Business'),
        ('asset', 'Asset/Equipment'),
        ('person', 'Personal'),
        ('service', 'Service'),
        ('other', 'Other'),
    ]
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gateways'
    )
    owner_name = models.CharField(max_length=200, blank=True)  # Owner's name for display
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    context_type = models.CharField(max_length=20, choices=CONTEXT_CHOICES)
    
    # Location and identification
    location_name = models.CharField(max_length=200, blank=True)
    identifier_text = models.CharField(max_length=100, blank=True)  # License plate, address, etc.
    
    # Settings
    is_emergency_enabled = models.BooleanField(default=True)
    auto_response_enabled = models.BooleanField(default=False)
    auto_response_message = models.TextField(blank=True)
    
    # Analytics
    total_interactions = models.PositiveIntegerField(default=0)
    last_interaction_at = models.DateTimeField(null=True, blank=True)
    
    # Distributor tracking
    distributor_code = models.CharField(max_length=20, blank=True, help_text="Distributor mobile number used during activation")
    
    class Meta:
        db_table = 'gateways'
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['context_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['identifier_text', 'is_active']),  # For vehicle number lookup
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_context_type_display()})"
    
    def get_primary_entry_point(self):
        """Get the primary entry point for this gateway."""
        return self.entry_points.filter(is_active=True).first()
    
    def get_public_url(self):
        """Get the public access URL for this gateway."""
        entry_point = self.get_primary_entry_point()
        if entry_point:
            return f"https://{settings.PLATFORM_DOMAIN}/g/{entry_point.public_identifier}/"
        return None
    
    def increment_interaction_count(self):
        """Increment the interaction counter."""
        from django.utils import timezone as django_timezone
        self.total_interactions += 1
        self.last_interaction_at = django_timezone.now()
        self.save(update_fields=['total_interactions', 'last_interaction_at'])


class EntryPoint(BaseModel):
    """
    Entry points for accessing gateways (QR codes, short links, etc.).
    """
    TYPE_CHOICES = [
        ('qr', 'QR Code'),
        ('shortlink', 'Short Link'),
        ('ivr', 'IVR Number'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    ]
    
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='entry_points'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    public_identifier = models.CharField(max_length=100, unique=True)
    
    # QR Code specific
    qr_code_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    
    # IVR specific
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Analytics
    access_count = models.PositiveIntegerField(default=0)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'entry_points'
        indexes = [
            models.Index(fields=['public_identifier']),
            models.Index(fields=['gateway', 'is_active']),
            models.Index(fields=['type']),
        ]
    
    def __str__(self):
        return f"{self.gateway.title} - {self.get_type_display()}"
    
    def save(self, *args, **kwargs):
        # Generate public identifier if not provided
        if not self.public_identifier:
            self.public_identifier = self.generate_identifier()
        
        super().save(*args, **kwargs)
        
        # Generate QR code for QR type entry points
        if self.type == 'qr' and not self.qr_code_image:
            self.generate_qr_code()
    
    def generate_identifier(self):
        """Generate a unique public identifier."""
        while True:
            identifier = generate_short_code(8)
            if not EntryPoint.objects.filter(public_identifier=identifier).exists():
                return identifier
    
    def generate_qr_code(self):
        """Generate QR code image."""
        if self.type == 'qr':
            url = f"https://{settings.PLATFORM_DOMAIN}/g/{self.public_identifier}/"
            qr_image = generate_qr_code(url)
            self.qr_code_image.save(
                f'qr_{self.public_identifier}.png',
                qr_image,
                save=True
            )
    
    def get_access_url(self):
        """Get the access URL for this entry point."""
        return f"https://{settings.PLATFORM_DOMAIN}/g/{self.public_identifier}/"
    
    def increment_access_count(self):
        """Increment the access counter."""
        from django.utils import timezone as django_timezone
        self.access_count += 1
        self.last_accessed_at = django_timezone.now()
        self.save(update_fields=['access_count', 'last_accessed_at'])


class GatewaySettings(models.Model):
    """
    Additional settings for gateways.
    """
    gateway = models.OneToOneField(
        Gateway,
        on_delete=models.CASCADE,
        related_name='settings'
    )
    
    # Communication preferences
    preferred_channels = models.JSONField(default=list)  # ['sms', 'whatsapp', 'ivr']
    blocked_channels = models.JSONField(default=list)
    
    # Time restrictions
    available_start_time = models.TimeField(null=True, blank=True)
    available_end_time = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Rate limiting
    max_interactions_per_hour = models.PositiveIntegerField(default=10)
    max_interactions_per_day = models.PositiveIntegerField(default=50)
    
    # Auto-responses
    welcome_message = models.TextField(blank=True)
    offline_message = models.TextField(blank=True)
    
    # Privacy settings
    log_interactions = models.BooleanField(default=True)
    store_contact_info = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gateway_settings'


class GatewayAnalytics(models.Model):
    """
    Analytics data for gateways.
    """
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    date = models.DateField()
    
    # Interaction metrics
    total_interactions = models.PositiveIntegerField(default=0)
    successful_interactions = models.PositiveIntegerField(default=0)
    blocked_interactions = models.PositiveIntegerField(default=0)
    
    # Channel breakdown
    sms_interactions = models.PositiveIntegerField(default=0)
    whatsapp_interactions = models.PositiveIntegerField(default=0)
    ivr_interactions = models.PositiveIntegerField(default=0)
    
    # Entry point breakdown
    qr_accesses = models.PositiveIntegerField(default=0)
    shortlink_accesses = models.PositiveIntegerField(default=0)
    
    # Geographic data (if available)
    top_countries = models.JSONField(default=dict)
    top_cities = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gateway_analytics'
        unique_together = ['gateway', 'date']
        indexes = [
            models.Index(fields=['gateway', 'date']),
        ]
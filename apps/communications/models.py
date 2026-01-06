"""
Communication models for tracking provider configurations and logs.
"""
from django.db import models
from django.utils import timezone as django_timezone


class CommunicationProvider(models.Model):
    """
    Configuration for communication providers.
    """
    PROVIDER_CHOICES = [
        ('twilio_sms', 'Twilio SMS'),
        ('twilio_voice', 'Twilio Voice'),
        ('whatsapp_business', 'WhatsApp Business API'),
        ('django_email', 'Django Email Backend'),
        ('custom', 'Custom Provider'),
    ]
    
    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    is_active = models.BooleanField(default=True)
    
    # Configuration (encrypted in production)
    configuration = models.JSONField(default=dict)
    
    # Limits and quotas
    daily_limit = models.PositiveIntegerField(null=True, blank=True)
    monthly_limit = models.PositiveIntegerField(null=True, blank=True)
    rate_limit_per_minute = models.PositiveIntegerField(default=10)
    
    # Usage tracking
    daily_usage = models.PositiveIntegerField(default=0)
    monthly_usage = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateField(default=django_timezone.now)
    
    # Status
    last_test_at = models.DateTimeField(null=True, blank=True)
    last_test_success = models.BooleanField(default=False)
    last_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'communication_providers'
        unique_together = ['name', 'provider_type']
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"
    
    def increment_usage(self):
        """Increment usage counters."""
        today = django_timezone.now().date()
        
        # Reset counters if it's a new day/month
        if self.last_reset_date < today:
            if self.last_reset_date.month != today.month:
                self.monthly_usage = 0
            self.daily_usage = 0
            self.last_reset_date = today
        
        self.daily_usage += 1
        self.monthly_usage += 1
        self.save(update_fields=['daily_usage', 'monthly_usage', 'last_reset_date'])
    
    def is_within_limits(self):
        """Check if provider is within usage limits."""
        if self.daily_limit and self.daily_usage >= self.daily_limit:
            return False
        if self.monthly_limit and self.monthly_usage >= self.monthly_limit:
            return False
        return True


class CommunicationLog(models.Model):
    """
    Log of all communication attempts.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]
    
    provider = models.ForeignKey(
        CommunicationProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Message details
    channel = models.CharField(max_length=20)
    recipient = models.CharField(max_length=255)
    message_content = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_id = models.CharField(max_length=255, blank=True)
    
    # Timing
    created_at = models.DateTimeField(default=django_timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Cost tracking
    cost_amount = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    cost_currency = models.CharField(max_length=3, default='USD')
    
    # Provider response
    provider_response = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'communication_logs'
        indexes = [
            models.Index(fields=['channel', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.channel} to {self.recipient} - {self.status}"
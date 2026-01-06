"""
Routing rules and communication flow models.
"""
import uuid
from django.db import models
from django.utils import timezone as django_timezone
from apps.core.models import BaseModel
from apps.gateways.models import Gateway


class RoutingRule(BaseModel):
    """
    Rules that determine how communications are routed.
    """
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('ivr', 'IVR Call'),
        ('email', 'Email'),
    ]
    
    INTENT_CHOICES = [
        ('general', 'General Inquiry'),
        ('emergency', 'Emergency'),
        ('complaint', 'Complaint'),
        ('compliment', 'Compliment'),
        ('business', 'Business Inquiry'),
        ('support', 'Support Request'),
    ]
    
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='routing_rules'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.PositiveIntegerField(default=1)  # Lower number = higher priority
    
    # Conditions
    allowed_channels = models.JSONField(default=list)  # ['sms', 'whatsapp']
    allowed_intents = models.JSONField(default=list)   # ['general', 'emergency']
    
    # Time restrictions
    time_window_start = models.TimeField(null=True, blank=True)
    time_window_end = models.TimeField(null=True, blank=True)
    allowed_days = models.JSONField(default=list)  # [1, 2, 3, 4, 5] for weekdays
    
    # Rate limiting
    max_requests_per_hour = models.PositiveIntegerField(null=True, blank=True)
    max_requests_per_day = models.PositiveIntegerField(null=True, blank=True)
    
    # Emergency handling
    emergency_only = models.BooleanField(default=False)
    emergency_escalation = models.BooleanField(default=False)
    
    # Actions
    forward_to_channels = models.JSONField(default=list)  # Channels to forward to
    auto_response_message = models.TextField(blank=True)
    require_approval = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'routing_rules'
        indexes = [
            models.Index(fields=['gateway', 'priority', 'is_active']),
            models.Index(fields=['emergency_only']),
        ]
        ordering = ['priority', 'created_at']
    
    def __str__(self):
        return f"{self.gateway.title} - {self.name}"
    
    def is_applicable(self, channel, intent, current_time=None):
        """Check if this rule applies to the given conditions."""
        if not self.is_active:
            return False
        
        # Check channel
        if self.allowed_channels and channel not in self.allowed_channels:
            return False
        
        # Check intent
        if self.allowed_intents and intent not in self.allowed_intents:
            return False
        
        # Check emergency only
        if self.emergency_only and intent != 'emergency':
            return False
        
        # Check time window
        if current_time and self.time_window_start and self.time_window_end:
            if not (self.time_window_start <= current_time <= self.time_window_end):
                return False
        
        # Check allowed days
        if current_time and self.allowed_days:
            weekday = current_time.weekday() + 1  # Monday = 1
            if weekday not in self.allowed_days:
                return False
        
        return True
    
    def check_rate_limits(self, ip_address=None):
        """Check if rate limits are exceeded."""
        from django.core.cache import cache
        
        now = django_timezone.now()
        
        # Check hourly limit
        if self.max_requests_per_hour:
            hour_key = f"routing_rule_{self.id}_hour_{now.hour}_{ip_address or 'global'}"
            hourly_count = cache.get(hour_key, 0)
            if hourly_count >= self.max_requests_per_hour:
                return False
        
        # Check daily limit
        if self.max_requests_per_day:
            day_key = f"routing_rule_{self.id}_day_{now.date()}_{ip_address or 'global'}"
            daily_count = cache.get(day_key, 0)
            if daily_count >= self.max_requests_per_day:
                return False
        
        return True
    
    def increment_usage(self, ip_address=None):
        """Increment usage counters."""
        from django.core.cache import cache
        
        now = django_timezone.now()
        
        # Increment hourly counter
        if self.max_requests_per_hour:
            hour_key = f"routing_rule_{self.id}_hour_{now.hour}_{ip_address or 'global'}"
            cache.set(hour_key, cache.get(hour_key, 0) + 1, 3600)
        
        # Increment daily counter
        if self.max_requests_per_day:
            day_key = f"routing_rule_{self.id}_day_{now.date()}_{ip_address or 'global'}"
            cache.set(day_key, cache.get(day_key, 0) + 1, 86400)


class BlockedContact(models.Model):
    """
    Blocked contacts and IP addresses.
    """
    BLOCK_TYPE_CHOICES = [
        ('ip', 'IP Address'),
        ('phone', 'Phone Number'),
        ('email', 'Email Address'),
        ('user_agent', 'User Agent'),
    ]
    
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='blocked_contacts'
    )
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES)
    value = models.CharField(max_length=255)  # IP, phone, email, etc.
    reason = models.TextField(blank=True)
    
    # Auto-expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    blocked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'blocked_contacts'
        unique_together = ['gateway', 'block_type', 'value']
        indexes = [
            models.Index(fields=['gateway', 'block_type']),
            models.Index(fields=['value']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.gateway.title} - Blocked {self.get_block_type_display()}: {self.value}"
    
    def is_active(self):
        """Check if the block is still active."""
        if self.expires_at and django_timezone.now() > self.expires_at:
            return False
        return True


class CommunicationTemplate(models.Model):
    """
    Templates for automated responses.
    """
    TEMPLATE_TYPE_CHOICES = [
        ('welcome', 'Welcome Message'),
        ('offline', 'Offline Message'),
        ('blocked', 'Blocked Message'),
        ('rate_limit', 'Rate Limit Message'),
        ('emergency', 'Emergency Response'),
        ('auto_reply', 'Auto Reply'),
    ]
    
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='communication_templates'
    )
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    
    # Content
    subject = models.CharField(max_length=200, blank=True)  # For email
    message = models.TextField()
    
    # Conditions
    channels = models.JSONField(default=list)  # Channels this template applies to
    intents = models.JSONField(default=list)   # Intents this template applies to
    
    # Settings
    is_active = models.BooleanField(default=True)
    send_delay_seconds = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'communication_templates'
        unique_together = ['gateway', 'template_type', 'name']
        indexes = [
            models.Index(fields=['gateway', 'template_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.gateway.title} - {self.name}"
    
    def is_applicable(self, channel, intent):
        """Check if this template applies to the given conditions."""
        if not self.is_active:
            return False
        
        if self.channels and channel not in self.channels:
            return False
        
        if self.intents and intent not in self.intents:
            return False
        
        return True


class RoutingLog(models.Model):
    """
    Log of routing decisions and actions.
    """
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='routing_logs'
    )
    routing_rule = models.ForeignKey(
        RoutingRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Request details
    channel = models.CharField(max_length=20)
    intent = models.CharField(max_length=20)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Routing decision
    action_taken = models.CharField(max_length=50)  # 'forwarded', 'blocked', 'rate_limited', etc.
    forwarded_to_channels = models.JSONField(default=list)
    
    # Result
    success = models.BooleanField()
    error_message = models.TextField(blank=True)
    
    # Timing
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'routing_logs'
        indexes = [
            models.Index(fields=['gateway', 'created_at']),
            models.Index(fields=['action_taken']),
            models.Index(fields=['success']),
        ]